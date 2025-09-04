import os
import sys
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin import exceptions as firebase_exceptions
from datetime import datetime

# Initialize Firebase Admin if not already initialized
def initialize_firebase():
    # Load .env
    load_dotenv()

    # Path to service account key (relative to backend/)
    SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")

    if not firebase_admin._apps:
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            raise FileNotFoundError(f"Firebase service account key not found at {SERVICE_ACCOUNT_PATH}")
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)

    return firestore.client()

# Firestore client
db = initialize_firebase()

class FirebaseService:
    @staticmethod
    def create_user(email: str, password: str, name: str) -> str:
        """
        Create a user in Firebase Auth and create a corresponding document in Firestore 'users' collection.
        Returns the created user's UID.
        """
        try:
            user = auth.create_user( 
                email=email,
                password=password,
                display_name=name
            )

            user_data = {
                'uid': user.uid,
                'email': email,
                'name': name,
                'role': 'user',
                'profilePicture': '',
                'friends': [],
                'createdAt': datetime.utcnow()
            }

            db.collection('users').document(user.uid).set(user_data)

            return user.uid
        except firebase_exceptions.FirebaseError as e:
            # Surface Firebase errors with message
            raise Exception(f"Firebase error creating user: {e}")
        except Exception as e:
            raise Exception(f"Error creating user: {e}")

    @staticmethod
    def verify_token(id_token: str) -> str | None:
        """
        Verify Firebase ID token. Returns uid if valid, otherwise None.
        """
        try:
            decoded = auth.verify_id_token(id_token)
            return decoded.get('uid')
        except Exception:
            return None

    @staticmethod
    def get_user(uid: str) -> dict | None:
        """
        Return Firestore user document as dict, or None if not found.
        """
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None

    @staticmethod
    def timestamp_now():
        return datetime.utcnow()