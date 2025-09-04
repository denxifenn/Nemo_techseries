import os
import sys
from typing import List, Dict

# Deterministic seeding of Firebase Auth users and Firestore user docs
# Usage (Windows Git Bash from repo root):
#   .venv/Scripts/python NemoApp/backend/scripts/seed_auth_users.py
#
# This will:
# - Ensure users user1, user2, user3 exist in Firebase Auth with email+password login
# - Set their UIDs deterministically to "user1", "user2", "user3"
# - Mirror/update Firestore users/{uid} docs (idempotent)
# - Set user1 role=admin, others role=user
#
# Emails and passwords are standardized for testing:
# - user1@nemoapp.local / Password123!
# - user2@nemoapp.local / Password123!
# - user3@nemoapp.local / Password123!

def main():
    service_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'firebase', 'firebase-admin-key.json')
    )
    if not os.path.exists(service_path):
        print('[ERROR] Service account JSON not found at', service_path)
        sys.exit(1)

    # Lazy import after basic checks
    import firebase_admin
    from firebase_admin import credentials, auth, firestore

    if not firebase_admin._apps:
        cred = credentials.Certificate(service_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    USERS: List[Dict] = [
        {
            "uid": "user1",
            "email": "user1@nemoapp.local",
            "password": "Password123!",
            "name": "Nemo Admin",
            "role": "admin",
        },
        {
            "uid": "user2",
            "email": "user2@nemoapp.local",
            "password": "Password123!",
            "name": "Nemo User Two",
            "role": "user",
        },
        {
            "uid": "user3",
            "email": "user3@nemoapp.local",
            "password": "Password123!",
            "name": "Nemo User Three",
            "role": "user",
        },
    ]

    created = []
    updated = []
    mirrored = []
    warnings = []
    errors = []

    for u in USERS:
        uid = u["uid"]
        email = u["email"]
        password = u["password"]
        name = u["name"]
        role = u["role"]

        # 1) Ensure Firebase Auth account exists with deterministic UID
        auth_user = None
        try:
            auth_user = auth.get_user(uid)
            # Align email/display_name/password to our standard values
            try:
                auth.update_user(uid, email=email, display_name=name, password=password)
                updated.append(uid)
            except Exception as e_upd:
                warnings.append(f"[WARN] Could not update auth user {uid}: {e_upd}")
        except auth.UserNotFoundError:
            # Create with exact UID
            try:
                auth_user = auth.create_user(uid=uid, email=email, password=password, display_name=name)
                created.append(uid)
            except Exception as e_create:
                errors.append(f"[ERROR] Failed to create auth user {uid}: {e_create}")
                continue
        except Exception as e_get:
            errors.append(f"[ERROR] Unexpected error fetching auth user {uid}: {e_get}")
            continue

        # 2) Mirror/update Firestore users/{uid} document
        try:
            doc_ref = db.collection('users').document(uid)
            doc_ref.set({
                "uid": uid,
                "email": email,
                "name": name,
                "role": role,
                "profilePicture": "",
                "friends": [],
            }, merge=True)
            mirrored.append(uid)
        except Exception as e_fs:
            errors.append(f"[ERROR] Failed to mirror Firestore user {uid}: {e_fs}")

    # Summary
    print("==== Seed Auth Users Summary ====")
    print("Created (auth):", created)
    print("Updated (auth):", updated)
    print("Mirrored (firestore):", mirrored)
    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    if errors:
        sys.exit(2)
    print("[PASS] Deterministic users seeded.")
    sys.exit(0)


if __name__ == "__main__":
    main()