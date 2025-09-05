import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin import exceptions as firebase_exceptions
from datetime import datetime
import os
from utils.phone_utils import is_phone_email, email_to_phone

# Path to service account key (override with env FIREBASE_CREDENTIALS_PATH)
DEFAULT_SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase', 'firebase-admin-key.json')
SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', DEFAULT_SERVICE_ACCOUNT_PATH)

# Initialize Firebase Admin if not already initialized
def initialize_firebase():
    if not firebase_admin._apps:
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            raise FileNotFoundError(
                f"Firebase service account key not found at {SERVICE_ACCOUNT_PATH}. "
                "Set FIREBASE_CREDENTIALS_PATH to the absolute path of your service account JSON."
            )
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
    def ensure_user_doc(uid: str, email: str | None = None, name: str | None = None, phoneNumber: str | None = None) -> dict:
        """
        Ensure a Firestore users/{uid} document exists.
        - If missing: create with sensible defaults (role=user, friends=[], profilePicture='')
          using provided email/name or fetched via Admin SDK.
        - If exists: backfill core fields (uid, email/name/phoneNumber if absent, role default) without clobbering others.
        Returns the user document as dict.
        """
        try:
            doc_ref = db.collection('users').document(uid)
            snap = doc_ref.get()

            if not snap.exists:
                # Attempt to enrich from Admin SDK if not provided
                if not email or not name:
                    try:
                        user = auth.get_user(uid)
                        email = email or getattr(user, 'email', None)
                        name = name or getattr(user, 'display_name', None)
                    except Exception:
                        pass

                # Infer phone from provided phoneNumber or email alias
                inferred_phone = None
                if phoneNumber:
                    inferred_phone = str(phoneNumber).strip()
                elif email and is_phone_email(email):
                    inferred_phone = email_to_phone(email)

                user_data = {
                    'uid': uid,
                    'email': email or '',
                    'phoneNumber': inferred_phone or '',
                    'name': (name or '').strip(),
                    'role': 'user',
                    'profilePicture': '',
                    'friends': [],
                    'createdAt': FirebaseService.timestamp_now()
                }
                doc_ref.set(user_data)
                ret = dict(user_data)
                ret['id'] = uid
                return ret

            # If exists, merge minimal defaults for missing fields
            data = snap.to_dict() or {}
            updates = {}
            if 'uid' not in data:
                updates['uid'] = uid
            if email and not data.get('email'):
                updates['email'] = email
            if name and not data.get('name'):
                updates['name'] = (name or '').strip()

            # Phone number handling: prefer explicit phoneNumber, otherwise infer from email alias
            if phoneNumber and not data.get('phoneNumber'):
                updates['phoneNumber'] = str(phoneNumber).strip()
            elif 'phoneNumber' not in data and email and is_phone_email(email):
                updates['phoneNumber'] = email_to_phone(email)

            if not data.get('role'):
                updates['role'] = 'user'
            if 'friends' not in data:
                updates['friends'] = []
            if 'profilePicture' not in data:
                updates['profilePicture'] = ''

            if updates:
                doc_ref.set(updates, merge=True)
                data.update(updates)

            data['id'] = snap.id
            return data
        except Exception:
            # Fallback minimal representation
            minimal_phone = None
            if phoneNumber:
                minimal_phone = str(phoneNumber).strip()
            elif email and is_phone_email(email):
                minimal_phone = email_to_phone(email)

            minimal = {
                'uid': uid,
                'email': email or '',
                'phoneNumber': minimal_phone or '',
                'name': (name or '').strip(),
                'role': 'user',
                'friends': [],
                'profilePicture': ''
            }
            minimal['id'] = uid
            return minimal

    @staticmethod
    def timestamp_now():
        return datetime.utcnow()