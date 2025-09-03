import os
import sys
import json
import time
from datetime import datetime
import traceback

# Verification script for Firebase Admin setup.
# Run from anywhere:
#   python NemoApp/backend/scripts/verify_firebase.py

def main():
    errors = []
    warnings = []

    # 1) Locate service account key
    service_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'firebase', 'firebase-admin-key.json')
    )
    print(f"[INFO] Looking for service account at: {service_path}")

    if not os.path.exists(service_path):
        print("[ERROR] Service account file not found.")
        print("        Expected at NemoApp/firebase/firebase-admin-key.json")
        sys.exit(1)

    # 2) Parse and sanity-check JSON fields
    try:
        with open(service_path, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
        project_id = key_data.get('project_id')
        client_email = key_data.get('client_email')
        private_key = key_data.get('private_key')
        print(f"[OK] Loaded service account JSON")
        print(f"     project_id: {project_id}")
        print(f"     client_email: {client_email}")
        if not project_id or not client_email or not private_key:
            errors.append("Service account JSON missing required fields (project_id/client_email/private_key).")
        elif not private_key.strip().startswith("-----BEGIN PRIVATE KEY-----"):
            warnings.append("private_key format unexpected; it should start with '-----BEGIN PRIVATE KEY-----'.")
    except Exception as e:
        print("[ERROR] Failed to read/parse service account JSON:", e)
        traceback.print_exc()
        sys.exit(1)

    # 3) Initialize Firebase Admin
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, auth
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_path)
            firebase_admin.initialize_app(cred)
            print("[OK] Initialized Firebase Admin SDK")
        else:
            print("[OK] Firebase Admin SDK already initialized (reusing existing app)")
    except Exception as e:
        print("[ERROR] Failed to initialize Firebase Admin SDK:", e)
        traceback.print_exc()
        sys.exit(1)

    # 4) Firestore connectivity test (write → read → delete)
    fs_ok = False
    try:
        from firebase_admin import firestore
        db = firestore.client()
        coll = "connectivity_test"
        doc_id = f"run_{int(time.time())}"
        data = {"status": "ok", "ts": datetime.utcnow().isoformat()}

        print(f"[INFO] Writing test document: {coll}/{doc_id}")
        db.collection(coll).document(doc_id).set(data)

        snap = db.collection(coll).document(doc_id).get()
        if not snap.exists:
            errors.append("Test document not found after write.")
        else:
            read_data = snap.to_dict()
            if read_data.get("status") == "ok":
                fs_ok = True
                print("[OK] Firestore write/read verified")
            else:
                errors.append("Read data did not match expected content.")

        print("[INFO] Deleting test document")
        db.collection(coll).document(doc_id).delete()
    except Exception as e:
        print("[ERROR] Firestore connectivity test failed:", e)
        traceback.print_exc()

    # 5) Auth Admin check (list first user, if any)
    auth_ok = False
    try:
        count = 0
        for _user in auth.list_users().iterate_all():
            count += 1
            break  # only need to hit the endpoint once
        print(f"[OK] Firebase Auth admin access verified (users_seen={count})")
        auth_ok = True
    except Exception as e:
        print("[ERROR] Firebase Auth admin access failed:", e)
        traceback.print_exc()

    # 6) Summary
    print("\n===== Firebase Verification Summary =====")
    if errors:
        for e in errors:
            print("[ERROR]", e)
    if warnings:
        for w in warnings:
            print("[WARN]", w)

    print(f"[RESULT] Firestore OK: {fs_ok}")
    print(f"[RESULT] Auth Admin OK: {auth_ok}")

    if errors or not fs_ok:
        print("\n[FAIL] Firebase Admin verification failed. See errors above.")
        sys.exit(2)

    print("\n[PASS] Firebase Admin verification succeeded.")
    sys.exit(0)


if __name__ == "__main__":
    main()