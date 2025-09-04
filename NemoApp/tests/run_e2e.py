import os
import json
import time
import sys
import requests

RAW_BASE_URL = os.environ.get('NEMO_BASE_URL', 'http://localhost:5000')
BASE_URL = (RAW_BASE_URL or '').strip().rstrip('/')
RAW_WEB_API_KEY = os.environ.get('NEMO_WEB_API_KEY', 'AIzaSyDsoT04meMxTii2hH7H1OcDWdLXbvPzM1I')
WEB_API_KEY = (RAW_WEB_API_KEY or '').strip()

EMAIL_USER = os.environ.get('NEMO_TEST_EMAIL', 'nemo.tester@example.com')
PASSWORD_USER = os.environ.get('NEMO_TEST_PASSWORD', 'Password123!')
EMAIL_FRIEND = os.environ.get('NEMO_FRIEND_EMAIL', 'nemo.friend@example.com')
PASSWORD_FRIEND = os.environ.get('NEMO_FRIEND_PASSWORD', 'Password123!')

def clean(s):
    return (s or '').strip()

def pretty(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)

def get_id_token(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={WEB_API_KEY}"
    payload = {"email": clean(email), "password": clean(password), "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        # Surface server error for diagnostics
        try:
            err_body = r.json()
        except Exception:
            err_body = r.text
        raise RuntimeError(f"signInWithPassword failed: {err_body}") from e
    j = r.json()
    return j.get('idToken'), j.get('localId')

def backend_register(email, password, name):
    url = f"{BASE_URL}/api/auth/register"
    payload = {"email": clean(email), "password": clean(password), "name": clean(name)}
    r = requests.post(url, json=payload, timeout=30)
    try:
        j = r.json()
    except Exception:
        j = {"raw": r.text}
    return r.status_code, j

def api(method, path, token=None, json_body=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    # Normalize path and compose URL safely
    path = path or ''
    if not path.startswith('/'):
        path = '/' + path
    url = f"{BASE_URL}{path}"
    r = requests.request(method, url, headers=headers, json=json_body, timeout=30)
    try:
        j = r.json()
    except Exception:
        j = {"raw": r.text}
    return r.status_code, j

def promote_user_to_admin_by_uid(uid):
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        script_dir = os.path.dirname(__file__)
        service_path = os.path.abspath(os.path.join(script_dir, '..', 'firebase', 'firebase-admin-key.json'))
        cred = credentials.Certificate(service_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    db.collection('users').document(uid).set({"role": "admin"}, merge=True)

def initialize_admin():
    import firebase_admin
    from firebase_admin import credentials
    if not firebase_admin._apps:
        script_dir = os.path.dirname(__file__)
        service_path = os.path.abspath(os.path.join(script_dir, '..', 'firebase', 'firebase-admin-key.json'))
        cred = credentials.Certificate(service_path)
        firebase_admin.initialize_app(cred)

def ensure_user_doc(uid, email, name, role='user'):
    from firebase_admin import firestore
    initialize_admin()
    db = firestore.client()
    db.collection('users').document(uid).set({
        "uid": uid,
        "email": clean(email),
        "name": clean(name),
        "role": role,
        "profilePicture": "",
        "friends": []
    }, merge=True)

def get_id_token_for_uid(uid):
    from firebase_admin import auth as admin_auth
    initialize_admin()
    custom_token = admin_auth.create_custom_token(uid)
    return exchange_custom_token(custom_token.decode('utf-8'))

def admin_get_uid_by_email(email):
    from firebase_admin import auth as admin_auth
    initialize_admin()
    user = admin_auth.get_user_by_email(clean(email))
    return user.uid

def exchange_custom_token(custom_token_b64):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={WEB_API_KEY}"
    payload = {"token": custom_token_b64, "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    j = r.json()
    return j.get('idToken'), j.get('localId')

def get_id_token_with_fallback(email, password):
    """
    Try normal password sign-in first. If disabled or fails, mint a custom token via Admin SDK and exchange for ID token.
    """
    try:
        return get_id_token(email, password)
    except Exception as e:
        # Attempt custom token flow
        import firebase_admin
        from firebase_admin import auth as admin_auth
        initialize_admin()
        try:
            try:
                uid = admin_get_uid_by_email(email)
            except Exception:
                # If user does not exist yet in Auth, create it now (password may be ignored if email/password sign-in disabled)
                user = admin_auth.create_user(email=clean(email), password=clean(password), display_name="Nemo QA")
                uid = user.uid
            custom_token = admin_auth.create_custom_token(uid)
            id_token, local_id = exchange_custom_token(custom_token.decode('utf-8'))
            return id_token, local_id
        except Exception as ce:
            raise RuntimeError(f"custom_token_flow failed: {repr(ce)}") from ce

def find_event_id(title_contains=None, exclude_full=True, prefer_category=None):
    status, data = api('GET', '/api/events')
    if status != 200:
        raise RuntimeError(f"Failed to list events: {status} {data}")
    events = data.get('events', [])
    candidates = events
    if prefer_category:
        candidates = [e for e in candidates if e.get('category') == prefer_category]
    if title_contains:
        candidates = [e for e in candidates if title_contains.lower() in (e.get('title') or '').lower()]
    if exclude_full:
        tmp = []
        for e in candidates:
            try:
                maxp = int(e.get('maxParticipants') or 0)
                cur = int(e.get('currentParticipants') or 0)
                if cur < maxp:
                    tmp.append(e)
            except Exception:
                tmp.append(e)
        candidates = tmp
    if not candidates and exclude_full:
        candidates = events
    if not candidates:
        raise RuntimeError("No events available")
    return candidates[0]['id'], candidates[0]

def main():
    results = {}
    code, reg = backend_register(EMAIL_USER, PASSWORD_USER, "Nemo Tester")
    results['register_user'] = {"status": code, "body": reg}
    uid_user = os.environ.get('NEMO_TEST_UID', 'qa_user_1')
    ensure_user_doc(uid_user, EMAIL_USER, "Nemo Tester")
    token_user, _ = get_id_token_for_uid(uid_user)
    results['idToken_user'] = {"uid": uid_user, "idToken_len": len(token_user or '')}
    code, body = api('GET', '/api/auth/verify', token_user)
    results['verify_user'] = {"status": code, "body": body}
    code, body = api('GET', '/api/profile', token_user)
    results['profile_get'] = {"status": code, "body": body}
    code, body = api('PUT', '/api/profile', token_user, {"name": "Nemo QA Runner"})
    results['profile_put'] = {"status": code, "body": body}
    ev_individual_id, ev_individual = find_event_id(title_contains="Football Match")
    code, body = api('POST', '/api/bookings/individual', token_user, {"eventId": ev_individual_id})
    results['booking_individual'] = {"status": code, "body": body}
    ev_group_id, ev_group = find_event_id(title_contains="Cooking Workshop", prefer_category="workshop")
    code, body = api('POST', '/api/bookings/group', token_user, {"eventId": ev_group_id, "groupMemberNames": ["Alice", "Bob"]})
    results['booking_group_names'] = {"status": code, "body": body}
    code, body = api('GET', '/api/bookings/my', token_user)
    results['bookings_my'] = {"status": code, "count": body.get('count'), "sample": (body.get('bookings') or [None])[0]}
    code, body = api('POST', '/api/suggestions', token_user, {"text": "Suggestions via QA runner"})
    results['suggestion_post'] = {"status": code, "body": body}
    promote_user_to_admin_by_uid(uid_user)
    code, body = api('GET', '/api/admin/health', token_user)
    results['admin_health'] = {"status": code, "body": body}
    title = f"QA Event {int(time.time())}"
    code, body = api('POST', '/api/admin/events', token_user, {
        "title": title,
        "description": "Automated QA created event",
        "category": "sports",
        "location": "Field A",
        "date": "2025-12-31",
        "time": "14:00",
        "maxParticipants": 20
    })
    results['admin_create_event'] = {"status": code, "body": body}
    # Ensure a friend account exists with a resolvable email; make unique when using default placeholder
    friend_email = EMAIL_FRIEND if EMAIL_FRIEND and EMAIL_FRIEND != 'nemo.friend@example.com' else f"nemo.friend+qa{int(time.time())}@example.com"
    code, reg2 = backend_register(friend_email, PASSWORD_FRIEND, "Nemo Friend")
    results['register_friend'] = {"status": code, "body": reg2}
    try:
        uid_friend = admin_get_uid_by_email(friend_email)
    except Exception:
        from firebase_admin import auth as admin_auth
        initialize_admin()
        user = admin_auth.create_user(email=friend_email, password=clean(PASSWORD_FRIEND), display_name="Nemo Friend")
        uid_friend = user.uid
    ensure_user_doc(uid_friend, friend_email, "Nemo Friend")
    token_friend, _ = get_id_token_for_uid(uid_friend)

    # Send and accept friend request
    code, body = api('POST', '/api/friends/request', token_user, {"email": friend_email})
    results['friend_request_send'] = {"status": code, "body": body}
    req_id = (body or {}).get('requestId')
    if req_id:
        code, body = api('PUT', f'/api/friends/request/{req_id}', token_friend, {"action": "accept"})
        results['friend_request_accept'] = {"status": code, "body": body}

    # Final friends list
    code, body = api('GET', '/api/friends', token_user)
    results['friends_list'] = {"status": code, "count": body.get('count'), "friends": body.get('friends')}
    print("===== QA RESULTS START =====")
    print(pretty(results))
    print("===== QA RESULTS END =====")

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print("QA runner failed:", repr(e))
        sys.exit(2)