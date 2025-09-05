from datetime import datetime, timedelta
from typing import List, Dict
import sys
import uuid

# Ensure this script is run from the backend/ directory:
#   python scripts/init_db.py
#
# Requires: firebase-admin-key.json placed at NemoApp/firebase/firebase-admin-key.json

try:
    # Import Firestore client from our Firebase service
    from services.firebase_service import db
except Exception as e:
    print("ERROR: Could not import Firestore client. Make sure you run this from backend/ directory.")
    print("Detail:", e)
    sys.exit(1)


def upsert_document(collection: str, doc_id: str, data: Dict) -> None:
    """
    Create the document only if it does not exist. If it exists, leave it unchanged.
    """
    doc_ref = db.collection(collection).document(doc_id)
    snap = doc_ref.get()
    if not snap.exists:
        doc_ref.set(data)


def seed_users():
    """
    Create a test admin and a test user in 'users' collection.
    Note: These are Firestore documents only. Firebase Auth accounts are created via your /api/auth/register
    or Firebase Console; admin endpoints require a valid idToken from Auth to pass require_admin().
    """
    now = datetime.utcnow()

    users = [
        {
            "id": "admin_test_001",
            "data": {
                "uid": "admin_test_001",
                "email": "admin@nemoapp.local",
                # Primary identifier in app flows remains phoneNumber
                "phoneNumber": "+6599990001",
                # Canonical full name (keep legacy 'name' for compatibility)
                "fullName": "Nemo Admin",
                "name": "Nemo Admin",
                # New profile fields
                "age": 30,
                "nationality": "Singaporean",
                "languages": ["English"],
                "homeCountry": "Singapore",
                "restDays": ["Saturday", "Sunday"],
                "interests": ["Community", "Events"],
                "skills": [{"name": "Organising", "rating": "Expert"}],
                # Completion flags
                "profileCompleted": True,
                "profileCompletedAt": now,
                # Existing fields
                "role": "admin",
                "profilePicture": "",
                "friends": [],
                "createdAt": now,
                "updatedAt": now,
            },
        },
        {
            "id": "user_test_001",
            "data": {
                "uid": "user_test_001",
                "email": "user@nemoapp.local",
                "phoneNumber": "+6599990002",
                "fullName": "Test User",
                "name": "Test User",
                "age": 25,
                "nationality": "Malaysian",
                "languages": ["English", "Malay"],
                "homeCountry": "Malaysia",
                "restDays": ["Sunday"],
                "interests": ["Football", "Cooking"],
                "skills": [{"name": "Cooking", "rating": "Proficient"}],
                "profileCompleted": True,
                "profileCompletedAt": now,
                "role": "user",
                "profilePicture": "",
                "friends": [],
                "createdAt": now,
                "updatedAt": now,
            },
        },
    ]

    for u in users:
        upsert_document("users", u["id"], u["data"])

    print("Seeded users: admin_test_001, user_test_001 (Firestore docs only)")


def seed_events():
    """
    Create several sample events in 'events' collection.
    """
    now = datetime.utcnow()
    base_date = now.date()

    sample_events: List[Dict] = [
        {
            "title": "Football Match",
            "description": "Friendly 5-a-side match.",
            "category": "sports",
            "imageUrl": "",
            "location": "Kallang Stadium",
            "date": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "time": "14:00",
            "maxParticipants": 20,
            "currentParticipants": 0,
            "participants": [],
            "createdBy": "admin_test_001",
            "status": "upcoming",
            "createdAt": now,
        },
        {
            "title": "Cooking Workshop",
            "description": "Learn to cook local dishes.",
            "category": "workshop",
            "imageUrl": "",
            "location": "Community Center A",
            "date": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "time": "10:00",
            "maxParticipants": 15,
            "currentParticipants": 0,
            "participants": [],
            "createdBy": "admin_test_001",
            "status": "upcoming",
            "createdAt": now,
        },
        {
            "title": "Cultural Gathering",
            "description": "Meet and share with friends.",
            "category": "social",
            "imageUrl": "",
            "location": "Downtown Hall",
            "date": (base_date + timedelta(days=8)).strftime("%Y-%m-%d"),
            "time": "18:30",
            "maxParticipants": 50,
            "currentParticipants": 0,
            "participants": [],
            "createdBy": "admin_test_001",
            "status": "upcoming",
            "createdAt": now,
        },
    ]

    created_ids = []
    events_col = db.collection("events")
    for ev in sample_events:
        # Use Firestore auto-ID; avoid duplicates by checking if an identical title/date already exists
        query = (
            events_col.where("title", "==", ev["title"])
            .where("date", "==", ev["date"])
            .limit(1)
            .stream()
        )
        existing = next(query, None)
        if existing:
            created_ids.append(existing.id)
        else:
            doc_ref = events_col.add(ev)[1]
            created_ids.append(doc_ref.id)

    print(f"Seeded events (count={len(created_ids)}): {created_ids}")


def seed_friend_requests():
    """
    Optionally seed a pending friend request from user_test_001 to admin_test_001.
    """
    now = datetime.utcnow()
    fr_col = db.collection("friendRequests")
    # Avoid duplicates: check if same sender/receiver pending exists
    query = (
        fr_col.where("fromUserId", "==", "user_test_001")
        .where("toUserId", "==", "admin_test_001")
        .where("status", "==", "pending")
        .limit(1)
        .stream()
    )
    existing = next(query, None)
    if not existing:
        fr_col.add(
            {
                "fromUserId": "user_test_001",
                "toUserId": "admin_test_001",
                "status": "pending",
                "createdAt": now,
            }
        )
        print("Seeded a pending friend request: user_test_001 -> admin_test_001")
    else:
        print("Friend request already exists (pending).")


def main():
    print("Initializing Firestore with sample data...")
    seed_users()
    seed_events()
    seed_friend_requests()
    print("Done. You can now implement Firestore logic in blueprints and query these documents.")


if __name__ == "__main__":
    main()