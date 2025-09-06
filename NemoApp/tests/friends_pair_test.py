import os
import sys
import json
import time
import requests

RAW_BASE_URL = os.environ.get("NEMO_BASE_URL", "http://localhost:5000")
BASE_URL = (RAW_BASE_URL or "").strip().rstrip("/")
WEB_API_KEY = os.environ.get("NEMO_WEB_API_KEY", "").strip()
PASSWORD = "Password123!"

def pretty(x):
    return json.dumps(x, indent=2, ensure_ascii=False)

def sign_in(email, password):
    if not WEB_API_KEY:
        raise RuntimeError("Missing NEMO_WEB_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={WEB_API_KEY}"
    r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=30)
    try:
        r.raise_for_status()
    except Exception:
        try:
            print("Sign-in error:", r.json())
        except Exception:
            print("Sign-in raw error:", r.text)
        raise
    j = r.json()
    return j.get("idToken"), j.get("localId")

def api(method, path, token=None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if not path.startswith("/"):
        path = "/" + path
    url = f"{BASE_URL}{path}"
    r = requests.request(method, url, headers=headers, json=body, timeout=30)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return r.status_code, data

def backend_register(email, password, name):
    return api("POST", "/api/auth/register", None, {"email": email, "password": password, "name": name})

def initialize_admin():
    import firebase_admin
    from firebase_admin import credentials
    if not firebase_admin._apps:
        script_dir = os.path.dirname(__file__)
        service_path = os.path.abspath(os.path.join(script_dir, "..", "firebase", "firebase-admin-key.json"))
        cred = credentials.Certificate(service_path)
        firebase_admin.initialize_app(cred)

def get_admin_db():
    initialize_admin()
    from firebase_admin import firestore as admin_fs
    return admin_fs.client()

def find_pending_request(from_uid, to_uid):
    try:
        db = get_admin_db()
        q = (
            db.collection("friendRequests")
            .where("fromUserId", "==", from_uid)
            .where("toUserId", "==", to_uid)
            .where("status", "==", "pending")
            .limit(1)
            .stream()
        )
        for doc in q:
            return doc.id
        return None
    except Exception:
        return None

def main():
    ts = int(time.time())
    email_a = f"user.a+{ts}@nemoapp.local"
    email_b = f"user.b+{ts}@nemoapp.local"
    name_a = "PairTest A"
    name_b = "PairTest B"

    results = {}

    # 1) Register user A (idempotent: accepts 201 or 400 if exists)
    code, j = backend_register(email_a, PASSWORD, name_a)
    if code not in (201, 400):
        raise RuntimeError(f"Unexpected register A status: {code}, body={j}")
    results["register_a"] = {"status": code, "body": j}

    # 2) Register user B
    code, j = backend_register(email_b, PASSWORD, name_b)
    if code not in (201, 400):
        raise RuntimeError(f"Unexpected register B status: {code}, body={j}")
    results["register_b"] = {"status": code, "body": j}

    # 3) Sign in both via email+password (explicit password-based auth as requested)
    token_a, uid_a = sign_in(email_a, PASSWORD)
    token_b, uid_b = sign_in(email_b, PASSWORD)
    results["signin_a"] = {"uid": uid_a, "token_len": len(token_a or "")}
    results["signin_b"] = {"uid": uid_b, "token_len": len(token_b or "")}

    # 4) Verify tokens
    code, j = api("GET", "/api/auth/verify", token_a)
    results["verify_a"] = {"status": code, "body": j}
    code, j = api("GET", "/api/auth/verify", token_b)
    results["verify_b"] = {"status": code, "body": j}

    # 5) A sends friend request to B (idempotent across reruns)
    code, j = api("POST", "/api/friends/request", token_a, {"email": email_b})
    results["friend_req_send"] = {"status": code, "body": j}
    req_id = None
    if code == 201:
        req_id = j.get("requestId")
    elif code == 400 and isinstance(j, dict) and "pending" in str(j.get("error", "")).lower():
        # Look up existing pending request from A -> B
        req_id = find_pending_request(uid_a, uid_b)

    # 6) B accepts friend request (if request id is known)
    if req_id:
        code, j = api("PUT", f"/api/friends/request/{req_id}", token_b, {"action": "accept"})
        results["friend_req_accept"] = {"status": code, "body": j}
    else:
        results["friend_req_accept"] = {"status": 400, "body": {"error": "No request id available"}}

    # 7) A lists friends
    code, j = api("GET", "/api/friends", token_a)
    results["friends_list_a"] = {"status": code, "count": j.get("count"), "friends": j.get("friends")}

    print("===== FRIENDS-PAIR TEST START =====")
    print(pretty(results))
    print("===== FRIENDS-PAIR TEST END =====")

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print("Friends-pair test failed:", repr(e))
        sys.exit(2)