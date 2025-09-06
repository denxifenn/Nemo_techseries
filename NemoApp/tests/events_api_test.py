import json
import sys
import time
import random
import string
import urllib.request
import urllib.error
from typing import Tuple

# Config
API_BASE_URL = "http://localhost:5000"
FIREBASE_API_KEY = "AIzaSyDsoT04meMxTii2hH7H1OcDWdLXbvPzM1I"  # from firebase-config.js
SERVICE_ACCOUNT_PATH = "NemoApp/firebase/firebase-admin-key.json"

PHONE_EMAIL_DOMAIN = "phone.local"


def http_request(method: str, url: str, body: dict | None = None, headers: dict | None = None, timeout: int = 30) -> Tuple[int, dict | str]:
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url=url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
            try:
                return resp.getcode(), json.loads(text)
            except Exception:
                return resp.getcode(), text
    except urllib.error.HTTPError as e:
        err_text = e.read().decode("utf-8", errors="ignore")
        try:
            return e.getcode(), json.loads(err_text)
        except Exception:
            return e.getcode(), err_text
    except Exception as e:
        return 0, {"error": str(e)}


# ------------- Phone helpers (no real emails, phone-as-email alias only) -------------
def only_digits(s: str) -> str:
    return "".join(ch for ch in str(s) if ch.isdigit())


def random_local8() -> str:
    # 8-digit number, first digit 8 or 9 for realism
    first = random.choice(["8", "9"])
    rest = "".join(random.choice(string.digits) for _ in range(7))
    return first + rest


def format_sg_phone(local8: str) -> str:
    d = only_digits(local8)
    if len(d) == 8:
        return f"+65{d}"
    if len(d) == 10 and d.startswith("65"):
        return f"+{d}"
    if len(d) == 11 and d.startswith("065"):
        return f"+{d[1:]}"
    raise ValueError(f"Invalid Singapore local phone: {local8}")


def phone_to_email_alias(e164_phone: str) -> str:
    # +6591234567 -> 6591234567@phone.local
    local = e164_phone.replace("+", "")
    return f"{local}@{PHONE_EMAIL_DOMAIN}"


# ------------- Firebase Auth (using phone-as-email alias) -------------
def firebase_signup_or_login_by_phone(phone_e164: str, password: str) -> tuple[str, str]:
    email_alias = phone_to_email_alias(phone_e164)

    # Try signUp first
    sign_up_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    code, data = http_request("POST", sign_up_url, {"email": email_alias, "password": password, "returnSecureToken": True})
    if code == 200 and isinstance(data, dict) and "idToken" in data:
        return data["idToken"], data.get("localId", "")

    # If exists, signIn
    sign_in_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    code, data = http_request("POST", sign_in_url, {"email": email_alias, "password": password, "returnSecureToken": True})
    if code == 200 and isinstance(data, dict) and "idToken" in data:
        return data["idToken"], data.get("localId", "")

    raise RuntimeError(f"Auth error for phone {phone_e164}: {data}")


# ------------- Firestore Admin helpers -------------
def set_admin_role(uid: str, phone_number: str, name: str = "Admin E2E"):
    """
    Use Admin SDK to ensure users/{uid}.role = admin.
    Stores no email; phone-only profile document.
    """
    import os
    import firebase_admin
    from firebase_admin import credentials, firestore

    svc_path = SERVICE_ACCOUNT_PATH
    if not os.path.exists(svc_path):
        raise FileNotFoundError(f"Service account JSON not found: {svc_path}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(svc_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    doc_ref = db.collection("users").document(uid)
    doc_ref.set(
        {
            "uid": uid,
            "phoneNumber": phone_number,
            "name": name,
            "fullName": name,
            "role": "admin",
            "profilePicture": "",
            "friends": [],
        },
        merge=True,
    )


# ------------- Backend helpers -------------
def backend_login(id_token: str, phone_number: str | None = None, name: str | None = None):
    url = f"{API_BASE_URL}/api/auth/login"
    body = {"idToken": id_token}
    if phone_number:
        body["phoneNumber"] = phone_number
    if name:
        body["name"] = name
    return http_request("POST", url, body)


def admin_create_event(admin_token: str) -> tuple[str, dict]:
    url = f"{API_BASE_URL}/api/admin/events"
    headers = {"Authorization": f"Bearer {admin_token}"}
    body = {
        "title": "API Test Event",
        "description": "Created by automated test",
        "format": "offline",
        "venueType": "indoor",
        "type": "music",
        "region": "central",
        "organiser": "Automated Tests",
        "location": "Test Venue",
        "date": "2099-12-31",
        "startTime": "18:30",
        "endTime": "20:00",
        "price": 0,
        "maxParticipants": 10,
        "imageUrl": ""
    }
    code, data = http_request("POST", url, body, headers=headers)
    if code != 201:
        raise RuntimeError(f"Admin create event failed: {code} {data}")
    return data.get("eventId"), body


def list_events(filters: dict | None = None):
    url = f"{API_BASE_URL}/api/events"
    if filters:
        import urllib.parse
        query = urllib.parse.urlencode(filters)
        url = f"{url}?{query}"
    return http_request("GET", url)


def get_event(event_id: str):
    return http_request("GET", f"{API_BASE_URL}/api/events/{event_id}")


def user_book_individual(user_token: str, event_id: str):
    headers = {"Authorization": f"Bearer {user_token}"}
    return http_request("POST", f"{API_BASE_URL}/api/bookings/individual", {"eventId": event_id}, headers=headers)


def user_book_group(user_token: str, event_id: str, names: list[str]):
    headers = {"Authorization": f"Bearer {user_token}"}
    body = {"eventId": event_id, "groupMemberNames": names}
    return http_request("POST", f"{API_BASE_URL}/api/bookings/group", body, headers=headers)


def user_cancel_by_event(user_token: str, event_id: str):
    headers = {"Authorization": f"Bearer {user_token}"}
    return http_request("DELETE", f"{API_BASE_URL}/api/bookings/by-event/{event_id}", headers=headers)


def admin_update_event(admin_token: str, event_id: str, updates: dict):
    headers = {"Authorization": f"Bearer {admin_token}"}
    return http_request("PUT", f"{API_BASE_URL}/api/admin/events/{event_id}", updates, headers=headers)


def assert_ok(code, data, step):
    if 200 <= code < 300:
        return
    raise RuntimeError(f"[{step}] failed: code={code} data={data}")


def main():
    print("=== Events API E2E (phone-only accounts) ===")

    # 0) Create admin and user accounts via phone-as-email alias (no real emails)
    password = "Password123!"
    admin_local = random_local8()
    user_local = random_local8()
    admin_phone = format_sg_phone(admin_local)
    user_phone = format_sg_phone(user_local)

    print(f"[1] Sign up/login admin (phone {admin_phone})...")
    admin_token, admin_uid = firebase_signup_or_login_by_phone(admin_phone, password)
    print(f"    - admin uid={admin_uid}")

    print("[2] Ensure admin role on Firestore (phone-only doc)...")
    set_admin_role(admin_uid, phone_number=admin_phone, name="Admin E2E")

    print(f"[3] Sign up/login regular user (phone {user_phone})...")
    user_token, user_uid = firebase_signup_or_login_by_phone(user_phone, password)
    print(f"    - user uid={user_uid}")

    # Provision user profile doc with phone (backend will create users/{uid})
    print("[4] Backend login (provision user doc)...")
    code, data = backend_login(user_token, phone_number=user_phone, name="User E2E")
    assert_ok(code, data, "backend_login")
    print(f"    - provisioned user (phoneNumber?): {data}")

    # Optional: provision admin in backend too (to set phoneNumber field if desired)
    try:
        backend_login(admin_token, phone_number=admin_phone, name="Admin E2E")
        time.sleep(0.2)
    except Exception:
        pass

    # Small delay
    time.sleep(0.4)

    # 1) Admin creates event
    print("[5] Admin create event...")
    event_id, create_payload = admin_create_event(admin_token)
    print(f"    - created eventId={event_id}")

    # 2) List events with filters
    print("[6] List events (filters: type=music, region=central)...")
    code, data = list_events({"type": "music", "region": "central", "fromDate": "2099-01-01"})
    assert_ok(code, data, "list_events")
    found = any(e.get("id") == event_id for e in (data.get("events") or []))
    print(f"    - event found in list: {found}")
    if not found:
        raise RuntimeError("Created event not found in list with filters")

    # 3) Get event and verify fields
    print("[7] Get event details...")
    code, data = get_event(event_id)
    assert_ok(code, data, "get_event")
    ev = (data or {}).get("event") or {}
    for k in ["format", "venueType", "type", "region", "organiser", "startTime", "endTime", "timing", "price"]:
        if ev.get(k) is None:
            raise RuntimeError(f"Field missing in event: {k}")
    if ev.get("availableSlots") is None:
        raise RuntimeError("availableSlots not present")
    print("    - event fields present")

    # 4) User books individual seat
    print("[8] User books individual seat...")
    code, data = user_book_individual(user_token, event_id)
    assert_ok(code, data, "book_individual")
    print(f"    - bookingId={data.get('bookingId')}")

    # 5) User books group with guest names
    print("[9] User books group with guest names...")
    code, data = user_book_group(user_token, event_id, ["Alice", "Bob"])
    assert_ok(code, data, "book_group")
    print(f"    - joinedCount={data.get('joinedCount')}")

    # 6) Get event again, check participants count increased (>=3 total added across steps)
    print("[10] Get event and verify counters...")
    code, data = get_event(event_id)
    assert_ok(code, data, "get_event_after_booking")
    ev2 = (data or {}).get("event") or {}
    cur = int(ev2.get("currentParticipants") or 0)
    if cur < 3:
        raise RuntimeError(f"Expected currentParticipants >= 3, got {cur}")
    avail = ev2.get("availableSlots")
    if avail is None:
        raise RuntimeError("availableSlots not computed in response")
    print(f"    - currentParticipants={cur}, availableSlots={avail}")

    # 7) Admin updates event (change start/end time and price)
    print("[11] Admin updates event (time and price)...")
    code, data = admin_update_event(admin_token, event_id, {"startTime": "19:00", "endTime": "21:00", "price": 5.5})
    assert_ok(code, data, "admin_update_event")
    print("    - update acknowledged")

    # 8) User cancels their booking by event
    print("[12] User cancels booking by event...")
    code, data = user_cancel_by_event(user_token, event_id)
    assert_ok(code, data, "cancel_by_event")
    print(f"    - seatsFreed={data.get('seatsFreed')}")

    # 9) Final list events (sanity)
    print("[13] Final list events (status=upcoming)...")
    code, data = list_events({"status": "upcoming"})
    assert_ok(code, data, "final_list")
    print(f"    - total returned: {len(data.get('events') or [])}")

    print("=== E2E OK: Events create/list/get/book/update/cancel verified ===")
    sys.exit(0)


if __name__ == "__main__":
    main()