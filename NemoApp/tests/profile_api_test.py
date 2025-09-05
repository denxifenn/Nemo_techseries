import json
import random
import string
import sys
import time
import urllib.request
import urllib.error

API_BASE_URL = "http://localhost:5000"
FIREBASE_API_KEY = "AIzaSyDsoT04meMxTii2hH7H1OcDWdLXbvPzM1I"  # from firebase-config.js
PHONE_EMAIL_DOMAIN = "phone.local"


def http_request(method: str, url: str, body: dict | None = None, headers: dict | None = None, timeout: int = 30):
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


def phone_to_email_alias(e164_phone: str) -> str:
    # +6591234567 -> 6591234567@phone.local
    local = e164_phone.replace("+", "")
    return f"{local}@{PHONE_EMAIL_DOMAIN}"


def random_sg_local() -> str:
    # 8-digit number, first digit 8 or 9 for realism
    first = random.choice(["8", "9"])
    rest = "".join(random.choice(string.digits) for _ in range(7))
    return first + rest


def normalize_sg_phone(local8: str) -> str:
    if not local8.isdigit() or len(local8) != 8:
        raise ValueError("local phone must be 8 digits")
    return "+65" + local8


def firebase_signup_or_login(email: str, password: str) -> tuple[str, str]:
    # Try signUp first
    sign_up_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    code, data = http_request("POST", sign_up_url, {"email": email, "password": password, "returnSecureToken": True})

    if code == 200 and isinstance(data, dict) and "idToken" in data:
        return data["idToken"], data.get("localId", "")

    # If exists, fall back to signInWithPassword
    sign_in_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    code, data = http_request("POST", sign_in_url, {"email": email, "password": password, "returnSecureToken": True})
    if code == 200 and isinstance(data, dict) and "idToken" in data:
        return data["idToken"], data.get("localId", "")

    raise RuntimeError(f"Firebase sign-up/sign-in failed: {data}")


def backend_login(id_token: str, phone_number: str, name: str | None = None):
    url = f"{API_BASE_URL}/api/auth/login"
    body = {"idToken": id_token, "phoneNumber": phone_number}
    if name:
        body["name"] = name
    return http_request("POST", url, body)


def get_profile(id_token: str):
    url = f"{API_BASE_URL}/api/profile"
    headers = {"Authorization": f"Bearer {id_token}"}
    return http_request("GET", url, headers=headers)


def update_profile(id_token: str, update_body: dict):
    url = f"{API_BASE_URL}/api/profile"
    headers = {"Authorization": f"Bearer {id_token}"}
    return http_request("PUT", url, body=update_body, headers=headers)


def completion_status(id_token: str):
    url = f"{API_BASE_URL}/api/profile/completion-status"
    headers = {"Authorization": f"Bearer {id_token}"}
    return http_request("GET", url, headers=headers)


def main():
    print("=== Nemo Profile API E2E ===")

    # 1) Create or login a Firebase user using phone-as-email alias
    local8 = random_sg_local()
    phone = normalize_sg_phone(local8)
    email_alias = phone_to_email_alias(phone)
    password = "Password123!"

    print(f"[1] Firebase Auth using email alias: {email_alias}")
    id_token, uid = firebase_signup_or_login(email_alias, password)
    print(f"    - Got ID token (length={len(id_token)}) UID={uid}")

    # 2) Backend login to provision Firestore profile
    print(f"[2] Backend login/provision for phone {phone}")
    code, data = backend_login(id_token, phone, name="API Tester")
    print(f"    - Response code={code}")
    print(f"    - Body: {json.dumps(data, indent=2, default=str)}")
    if code != 200:
        print("Backend login failed. Aborting.")
        sys.exit(2)

    # Small delay to let Firestore settle
    time.sleep(0.5)

    # 3) GET profile
    print("[3] GET /api/profile")
    code, data = get_profile(id_token)
    print(f"    - Response code={code}")
    print(f"    - Body: {json.dumps(data, indent=2, default=str)}")
    if code != 200:
        print("Get profile failed. Aborting.")
        sys.exit(3)

    # 4) PUT profile with required fields
    print("[4] PUT /api/profile with required + optional fields")
    update_body = {
        "fullName": "API Tester User",
        "age": 28,
        "nationality": "Singaporean",
        "languages": ["English", "Mandarin"],
        "homeCountry": "Singapore",
        "restDays": ["Saturday", "Sunday"],
        "interests": ["Football", "Cooking"],
        "skills": [
            {"name": "Cooking", "rating": "Proficient"},
            {"name": "Programming", "rating": "Expert"}
        ],
        "profilePicture": ""
    }
    code, data = update_profile(id_token, update_body)
    print(f"    - Response code={code}")
    print(f"    - Body: {json.dumps(data, indent=2, default=str)}")
    if code != 200:
        print("Update profile failed. Aborting.")
        sys.exit(4)

    # 5) Check completion status
    print("[5] GET /api/profile/completion-status")
    code, data = completion_status(id_token)
    print(f"    - Response code={code}")
    print(f"    - Body: {json.dumps(data, indent=2, default=str)}")
    if code != 200:
        print("Completion status check failed.")
        sys.exit(5)

    status = (data or {}).get("status", {})
    if status.get("profileCompleted"):
        print("=== E2E OK: Profile is completed ===")
        sys.exit(0)
    else:
        print("=== E2E WARNING: Profile not completed ===")
        sys.exit(6)


if __name__ == "__main__":
    main()