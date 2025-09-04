import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

# Ensure this script is run from the backend/ directory:
#   python scripts/init_db.py
#
# Requires: firebase-admin-key.json placed at NemoApp/firebase/firebase-admin-key.json

try:
    # Import Firestore client from our Firebase service
    # Add root directory to sys.path so 'services' becomes importable
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
                "name": "Nemo Admin",
                "role": "admin",
                "profilePicture": "",
                "friends": [],
                "createdAt": now,
            },
        },
        {
            "id": "user_test_001",
            "data": {
                "uid": "user_test_001",
                "email": "user@nemoapp.local",
                "name": "Test User",
                "role": "user",
                "profilePicture": "",
                "friends": [],
                "createdAt": now,
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
            "title": "",
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

def seed_suggestions():
    """
    Seed a suggestion from user_test_001 to admin_test_001 with restricted status values.
    """
    now = datetime.utcnow()
    suggestions_col = db.collection("suggestions")
    
    # Example suggestion data
    suggestions = [
        {
            # "title": "Cooking Workshop",
            "description": "Learn to cook local dishes",
            # "category": "workshop",
            # "status": "pending",  # Valid status
            "createdBy": "admin_test_001",  # Admin who created the event suggestion
            "userId": "user_test_001",  # User suggesting the event
        },
        {
            # "title": "Tech Conference",
            "description": "Join industry leaders for a tech conference",
            # "category": "workshop",
            # "status": "accepted",  # Valid status
            "createdBy": "admin_test_001",  # Admin who created the event suggestion
            "userId": "user_test_002",  # Another user suggesting the event
        },
        {
            # "title": "Yoga Retreat",
            "description": "A relaxing yoga retreat for mindfulness",
            # "category": "sports",  # Invalid category, should return an error in POST
            # "status": "rejected",  # Valid status
            "createdBy": "admin_test_002",  # Admin who created the event suggestion
            "userId": "user_test_003",  # Another user suggesting the event
        },
    ]
    
    # Get the total number of existing suggestions in the collection
    existing_suggestions_count = len(list(suggestions_col.stream()))
    
    for suggestion in suggestions:
        # Generate the new suggestion ID based on the count of existing suggestions
        suggestion_id = f"suggest{existing_suggestions_count + 1}"
        
        # Add suggestion document to Firestore with the generated sequential ID
        doc = {
            "userId": suggestion["userId"],
            # "eventTitle": suggestion["title"],
            "eventDescription": suggestion["description"],
            # "category": suggestion["category"],
            # "status": suggestion["status"],
            "createdBy": suggestion["createdBy"],
            "createdAt": now
        }
        
        # Insert the document into Firestore using the sequential ID
        doc_ref = suggestions_col.document(suggestion_id).set(doc)
        
        # Increment the suggestion count for the next suggestion ID
        existing_suggestions_count += 1
        
        print(f"Seeded suggestion with title: (UID: {suggestion_id})")

def main():
    print("Initializing Firestore with sample data...")
    seed_users()
    seed_events()
    seed_friend_requests()
    seed_suggestions()
    print("Done. You can now implement Firestore logic in blueprints and query these documents.")


if __name__ == "__main__":
    main()