import os
import json
import time
import sys
import requests

RAW_BASE_URL = os.environ.get('NEMO_BASE_URL', 'http://localhost:5000')
BASE_URL = (RAW_BASE_URL or '').strip().rstrip('/')
RAW_WEB_API_KEY = os.environ.get('NEMO_WEB_API_KEY', 'AIzaSyDsoT04meMxTii2hH7H1OcDWdLXbvPzM1I')
WEB_API_KEY = (RAW_WEB_API_KEY or '').strip()

EMAIL_USER = os.environ.get('NEMO_TEST_EMAIL', 'user1@nemoapp.local')
PASSWORD_USER = os.environ.get('NEMO_TEST_PASSWORD', 'Password123!')
EMAIL_FRIEND = os.environ.get('NEMO_FRIEND_EMAIL', 'user2@nemoapp.local')
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


def get_admin_db():
    initialize_admin()
    from firebase_admin import firestore as admin_fs
    return admin_fs.client()

def find_pending_friend_request(from_uid, to_uid):
    """
    Look up a pending friend request from 'from_uid' to 'to_uid'.
    Returns request_id or None.
    """
    try:
        db = get_admin_db()
        q = (
            db.collection('friendRequests')
              .where('fromUserId', '==', from_uid)
              .where('toUserId', '==', to_uid)
              .where('status', '==', 'pending')
              .limit(1)
              .stream()
        )
        for doc in q:
            return doc.id
        return None
    except Exception:
        return None
def get_admin_db():
    initialize_admin()
    from firebase_admin import firestore
    return firestore.client()

def find_pending_friend_request(from_uid, to_uid):
    """
    Look up a pending friend request from 'from_uid' to 'to_uid'.
    Returns request_id or None.
    """
    try:
        db = get_admin_db()
        q = (
            db.collection('friendRequests')
              .where('fromUserId', '==', from_uid)
              .where('toUserId', '==', to_uid)
              .where('status', '==', 'pending')
              .limit(1)
              .stream()
        )
        for doc in q:
            return doc.id
        return None
    except Exception:
        return None

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
    results['register_user'] = {"status": 200, "body": {"skipped": True, "reason": "using seeded user1"}}
    # Use robust sign-in with fallback to custom token if password sign-in is disabled
    token_user, uid_user = get_id_token_with_fallback(EMAIL_USER, PASSWORD_USER)
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
    # Use seeded user2 (email+password)
    results['register_friend'] = {"status": 200, "body": {"skipped": True, "reason": "using seeded user2"}}
    token_friend, uid_friend = get_id_token_with_fallback(EMAIL_FRIEND, PASSWORD_FRIEND)

    # Ensure there is a pending friend request from user1 -> user2 (idempotent across reruns)
    req_id = find_pending_friend_request(uid_user, uid_friend)
    if not req_id:
        code, body = api('POST', '/api/friends/request', token_user, {"email": EMAIL_FRIEND})
        results['friend_request_send'] = {"status": code, "body": body}
        if code == 201:
            req_id = (body or {}).get('requestId')
        elif code == 400 and isinstance(body, dict) and str(body.get('error', '')).lower().startswith('a pending request already exists'):
            # Re-query to fetch the existing pending request id
            req_id = find_pending_friend_request(uid_user, uid_friend)
    else:
        results['friend_request_send'] = {"status": 200, "body": {"reusedPending": True, "requestId": req_id}}

    # Accept pending request as user2 if available
    if req_id:
        code, body = api('PUT', f'/api/friends/request/{req_id}', token_friend, {"action": "accept"})
        results['friend_request_accept'] = {"status": code, "body": body}
    else:
        results['friend_request_accept'] = {"status": 400, "body": {"error": "No request id available"}}

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