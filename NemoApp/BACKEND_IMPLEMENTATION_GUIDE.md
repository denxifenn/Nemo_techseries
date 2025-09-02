
# Backend & Database Implementation Guide

## Your Responsibilities (Backend + Database)
As the backend developer, you're responsible for:
1. Firebase setup and configuration
2. Database schema and collections
3. All API endpoints
4. Authentication logic
5. Data validation and security

## Frontend Team Handoff
The frontend team will need:
- API endpoint documentation
- Authentication flow details
- Response/request formats
- CORS configuration

---

## Phase 1: Firebase & Database Setup

### Task KAN-5 & KAN-6: Firebase Integration

#### 1. Create Firebase Project
```bash
# Go to https://console.firebase.google.com/
# Create project named "nemo-app"
# Enable Authentication (Email/Password)
# Enable Firestore Database (test mode for now)
# Download service account key as firebase-admin-key.json
```

#### 2. Backend Firebase Service
```python
# backend/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from datetime import datetime

# Initialize Firebase Admin
cred = credentials.Certificate('../firebase/firebase-admin-key.json')
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

class FirebaseService:
    @staticmethod
    def create_user(email, password, name):
        """Create user in Firebase Auth and Firestore"""
        try:
            # Create in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            
            # Create in Firestore
            user_data = {
                'uid': user.uid,
                'email': email,
                'name': name,
                'role': 'user',
                'friends': [],
                'createdAt': datetime.now()
            }
            db.collection('users').document(user.uid).set(user_data)
            
            return user.uid
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    @staticmethod
    def verify_token(id_token):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token['uid']
        except:
            return None
```

### Tasks KAN-27 to KAN-32: Database Collections

#### Collection Schemas

```python
# backend/models/schemas.py
from datetime import datetime

# KAN-27: Users Collection
USER_SCHEMA = {
    'uid': str,  # Firebase Auth UID
    'email': str,
    'name': str,
    'role': str,  # 'user' or 'admin'
    'profilePicture': str,  # URL
    'friends': list,  # List of user UIDs
    'createdAt': datetime
}

# KAN-28: Events Collection  
EVENT_SCHEMA = {
    'eventId': str,  # Auto-generated
    'title': str,
    'description': str,
    'category': str,  # 'sports', 'workshop', 'social', 'cultural'
    'imageUrl': str,
    'location': str,
    'date': str,  # Format: "2025-03-15"
    'time': str,  # Format: "14:00"
    'maxParticipants': int,
    'currentParticipants': int,
    'participants': list,  # List of user UIDs
    'createdBy': str,  # Admin UID
    'status': str,  # 'upcoming', 'ongoing', 'completed', 'cancelled'
    'createdAt': datetime
}

# KAN-29: Bookings Collection
BOOKING_SCHEMA = {
    'bookingId': str,
    'eventId': str,
    'userId': str,
    'bookingType': str,  # 'individual' or 'group'
    'groupMembers': list,  # List of UIDs if group booking
    'status': str,  # 'confirmed', 'cancelled'
    'createdAt': datetime
}

# KAN-30: Friend Requests Collection
FRIEND_REQUEST_SCHEMA = {
    'requestId': str,
    'fromUserId': str,
    'toUserId': str,
    'status': str,  # 'pending', 'accepted', 'rejected'
    'createdAt': datetime
}

# KAN-31: Suggestions Collection
SUGGESTION_SCHEMA = {
    'suggestionId': str,
    'userId': str,
    'eventTitle': str,
    'eventDescription': str,
    'category': str,
    'status': str,  # 'pending', 'approved', 'rejected'
    'adminNotes': str,
    'createdAt': datetime
}

# KAN-32: Admin Collection (optional - can use role in users)
ADMIN_SCHEMA = {
    'adminId': str,
    'userId': str,
    'permissions': list,  # ['create_event', 'manage_users', 'review_suggestions']
    'createdAt': datetime
}
```

#### Initialize Collections Script
```python
# backend/scripts/init_db.py
from services.firebase_service import db
from datetime import datetime

def initialize_collections():
    """Create initial data for testing"""
    
    # Create test admin user
    admin_data = {
        'uid': 'admin_test_001',
        'email': 'admin@nemo.com',
        'name': 'Admin User',
        'role': 'admin',
        'friends': [],
        'createdAt': datetime.now()
    }
    db.collection('users').document('admin_test_001').set(admin_data)
    
    # Create sample events
    events = [
        {
            'title': 'Football Match',
            'description': 'Friendly football match at Kallang',
            'category': 'sports',
            'location': 'Kallang Stadium',
            'date': '2025-03-15',
            'time': '14:00',
            'maxParticipants': 20,
            'currentParticipants': 0,
            'participants': [],
            'createdBy': 'admin_test_001',
            'status': 'upcoming',
            'createdAt': datetime.now()
        },
        {
            'title': 'Cooking Workshop',
            'description': 'Learn to cook local dishes',
            'category': 'workshop',
            'location': 'Community Center',
            'date': '2025-03-20',
            'time': '10:00',
            'maxParticipants': 15,
            'currentParticipants': 0,
            'participants': [],
            'createdBy': 'admin_test_001',
            'status': 'upcoming',
            'createdAt': datetime.now()
        }
    ]
    
    for event in events:
        db.collection('events').add(event)
    
    print("Database initialized with sample data")

if __name__ == "__main__":
    initialize_collections()
```

---

## Phase 2: Authentication APIs

### Task KAN-7: Login & Register APIs

```python
# backend/api/auth.py
from flask import Blueprint, request, jsonify
from services.firebase_service import FirebaseService, auth, db
import firebase_admin.auth as firebase_auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # Validate input
        if not email or not password or not name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create user
        uid = FirebaseService.create_user(email, password, name)
        
        return jsonify({
            'success': True,
            'uid': uid,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint - Frontend handles Firebase Auth"""
    try:
        data = request.json
        token = data.get('idToken')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Verify token
        uid = FirebaseService.verify_token(token)
        if not uid:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get user data
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        
        return jsonify({
            'success': True,
            'user': {
                'uid': uid,
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'role': user_data.get('role')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """Verify if token is valid"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({'valid': False}), 401
    
    uid = FirebaseService.verify_token(token)
    if uid:
        return jsonify({'valid': True, 'uid': uid}), 200
    
    return jsonify({'valid': False}), 401
```

---

## Phase 3: Events APIs

### Tasks KAN-8, KAN-9: Events Endpoints

```python
# backend/api/events.py
from flask import Blueprint, request, jsonify
from services.firebase_service import db
from datetime import datetime
from utils.decorators import require_auth, require_admin

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        status = request.args.get('status', 'upcoming')
        
        # Build query
        events_ref = db.collection('events')
        
        if category:
            events_ref = events_ref.where('category', '==', category)
        if status:
            events_ref = events_ref.where('status', '==', status)
        
        # Execute query
        events = []
        for doc in events_ref.stream():
            event = doc.to_dict()
            event['id'] = doc.id
            events.append(event)
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get single event details"""
    try:
        event_ref = db.collection('events').document(event_id)
        event_doc = event_ref.get()
        
        if not event_doc.exists:
            return jsonify({'error': 'Event not found'}), 404
        
        event = event_doc.to_dict()
        event['id'] = event_doc.id
        
        return jsonify({
            'success': True,
            'event': event
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Phase 4: Booking APIs

### Tasks KAN-10, KAN-11: Booking Endpoints

```python
# backend/api/bookings.py
from flask import Blueprint, request, jsonify
from services.firebase_service import db
from datetime import datetime
from utils.decorators import require_auth

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/api/bookings/individual', methods=['POST'])
@require_auth
def create_individual_booking(current_user):
    """Create individual booking"""
    try:
        data = request.json
        event_id = data.get('eventId')
        
        # Check if event exists and has space
        event_ref = db.collection('events').document(event_id)
        event = event_ref.get()
        
        if not event.exists:
            return jsonify({'error': 'Event not found'}), 404
        
        event_data = event.to_dict()
        if event_data['currentParticipants'] >= event_data['maxParticipants']:
            return jsonify({'error': 'Event is full'}), 400
        
        # Check if user already booked
        existing = db.collection('bookings').where('userId', '==', current_user).where('eventId', '==', event_id).get()
        if len(existing) > 0:
            return jsonify({'error': 'Already booked for this event'}), 400
        
        # Create booking
        booking = {
            'eventId': event_id,
            'userId': current_user,
            'bookingType': 'individual',
            'status': 'confirmed',
            'createdAt': datetime.now()
        }
        
        booking_ref = db.collection('bookings').add(booking)
        
        # Update event participants
        event_ref.update({
            'currentParticipants': event_data['currentParticipants'] + 1,
            'participants': event_data.get('participants', []) + [current_user]
        })
        
        return jsonify({
            'success': True,
            'bookingId': booking_ref[1].id,
            'message': 'Booking confirmed'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/api/bookings/group', methods=['POST'])
@require_auth
def create_group_booking(current_user):
    """Create group booking"""
    try:
        data = request.json
        event_id = data.get('eventId')
        group_members = data.get('groupMembers', [])
        
        # Include the current user in the group
        all_members = [current_user] + group_members
        
        # Check event capacity
        event_ref = db.collection('events').document(event_id)
        event = event_ref.get()
        
        if not event.exists:
            return jsonify({'error': 'Event not found'}), 404
        
        event_data = event.to_dict()
        available_spots = event_data['maxParticipants'] - event_data['currentParticipants']
        
        if len(all_members) > available_spots:
            return jsonify({'error': f'Only {available_spots} spots available'}), 400
        
        # Create group booking
        booking = {
            'eventId': event_id,
            'userId': current_user,
            'bookingType': 'group',
            'groupMembers': all_members,
            'status': 'confirmed',
            'createdAt': datetime.now()
        }
        
        booking_ref = db.collection('bookings').add(booking)
        
        # Update event
        event_ref.update({
            'currentParticipants': event_data['currentParticipants'] + len(all_members),
            'participants': event_data.get('participants', []) + all_members
        })
        
        return jsonify({
            'success': True,
            'bookingId': booking_ref[1].id,
            'message': f'Group booking confirmed for {len(all_members)} people'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookings_bp.route('/api/bookings/my', methods=['GET'])
@require_auth
def get_my_bookings(current_user):
    """Get user's bookings"""
    try:
        bookings = []
        bookings_ref = db.collection('bookings').where('userId', '==', current_user)
        
        for doc in bookings_ref.stream():
            booking = doc.to_dict()
            booking['id'] = doc.id
            
            # Get event details
            event_doc = db.collection('events').document(booking['eventId']).get()
            if event_doc.exists:
                booking['event'] = event_doc.to_dict()
                booking['event']['id'] = event_doc.id
            
            bookings.append(booking)
        
        return jsonify({
            'success': True,
            'bookings': bookings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Phase 5: Profile & Friends APIs

### Tasks KAN-12, KAN-17, KAN-19: Profile and Friends

```python
# backend/api/profile.py
from flask import Blueprint, request, jsonify
from services.firebase_service import db
from utils.decorators import require_auth

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """Get user profile"""
    try:
        user_doc = db.collection('users').document(current_user).get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        
        return jsonify({
            'success': True,
            'profile': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/api/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """Update user profile"""
    try:
        data = request.json
        allowed_fields = ['name', 'profilePicture']
        
        updates = {}
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]
        
        if updates:
            db.collection('users').document(current_user).update(updates)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

```python
# backend/api/friends.py
from flask import Blueprint, request, jsonify
from services.firebase_service import db
from datetime import datetime
from utils.decorators import require_auth

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/api/friends/request', methods=['POST'])
@require_auth
def send_friend_request(current_user):
    """Send friend request"""
    try:
        data = request.json
        to_user_email = data.get('email')
        
        # Find user by email
        users = db.collection('users').where('email', '==', to_user_email).get()
        if len(users) == 0:
            return jsonify({'error': 'User not found'}), 404
        
        to_user = users[0]
        to_user_id = to_user.id
        
        # Check if already friends
        user_doc = db.collection('users').document(current_user).get()
        if to_user_id in user_doc.to_dict().get('friends', []):
            return jsonify({'error': 'Already friends'}), 400
        
        # Check if request already exists
        existing = db.collection('friendRequests').where('fromUserId', '==', current_user).where('toUserId', '==', to_user_id).where('status', '==', 'pending').get()
        if len(existing) > 0:
            return jsonify({'error': 'Request already sent'}), 400
        
        # Create request
        request_data = {
            'fromUserId': current_user,
            'toUserId': to_user_id,
            'status': 'pending',
            'createdAt': datetime.now()
        }
        
        request_ref = db.collection('friendRequests').add(request_data)
        
        return jsonify({
            'success': True,
            'requestId': request_ref[1].id,
            'message': 'Friend request sent'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/api/friends/request/<request_id>', methods=['PUT'])
@require_auth
def handle_friend_request(current_user, request_id):
    """Accept or reject friend request"""
    try:
        data = request.json
        action = data.get('action')  # 'accept' or 'reject'
        
        if action not in ['accept', 'reject']:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Get request
        request_ref = db.collection('friendRequests').document(request_id)
        request_doc = request_ref.get()
        
        if not request_doc.exists:
            return jsonify({'error': 'Request not found'}), 404
        
        request_data = request_doc.to_dict()
        
        # Verify user is the recipient
        if request_data['toUserId'] != current_user:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if action == 'accept':
            # Add each other as friends
            from_user_ref = db.collection('users').document(request_data['fromUserId'])
            to_user_ref = db.collection('users').document(request_data['toUserId'])
            
            # Update both users' friend lists
            from_user = from_user_ref.get().to_dict()
            to_user = to_user_ref.get().to_dict()
            
            from_user_friends = from_user.get('friends', [])
            to_user_friends = to_user.get('friends', [])
            
            from_user_friends.append(request_data['toUserId'])
            to_user_friends.append(request_data['fromUserId'])
            
            from_user_ref.update({'friends': from_user_friends})
            to_user_ref.update({'friends': to_user_friends})
            
            status = 'accepted'
        else:
            status = 'rejected'
        
        # Update request status
        request_ref.update({'status': status})
        
        return jsonify({
            'success': True,
            'message': f'Friend request {status}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/api/friends', methods=['GET'])
@require_auth
def get_friends(current_user):
    """Get user's friends list"""
    try:
        user_doc = db.collection('users').document(current_user).get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        friend_ids = user_doc.to_dict().get('friends', [])
        friends = []
        
        for friend_id in friend_ids:
            friend_doc = db.collection('users').document(friend_id).get()
            if friend_doc.exists:
                friend_data = friend_doc.to_dict()
                friends.append({
                    'id': friend_id,
                    'name': friend_data.get('name'),
                    'email': friend_data.get('email'),
                    'profilePicture': friend_data.get('profilePicture')
                })
        
        return jsonify({
            'success': True,
            'friends': friends
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Phase 6: Admin & Suggestions APIs

### Tasks KAN-21, KAN-23: Admin and Suggestions

```python
# backend/api/admin.py
from flask import Blueprint, request, jsonify
from services.firebase_service import db
from datetime import datetime
from utils.decorators import require_admin

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/events', methods=['POST'])
@require_admin
def create_event(current_user):
    """Create new event (admin only)"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['title', 'description', 'category', 'location', 'date', 'time', 'maxParticipants']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Create event
        event = {
            'title': data['title'],
            'description': data['description'],
            'category': data['category'],
            'imageUrl': data.get('imageUrl', ''),
            'location': data['location'],
            'date': data['date'],
            'time': data['time'],
            'maxParticipants': int(data['maxParticipants']),
            'currentParticipants': 0,
            'participants': [],
            'createdBy': current_user,
            'status': 'upcoming',
            'createdAt': datetime.now()
        }
        
        event_ref = db.collection('events').add(event)
        
        return jsonify({
            'success': True,
            'eventId': event_ref[1].id,
            'message': 'Event created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

```python
# backend/api/suggestions.py
from flask import Blueprint, request, jsonify
from services.firebase_service import db
from datetime import datetime
from utils.decorators import require_auth, require_admin

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/api/suggestions', methods=['POST'])
@require_auth
def create_suggestion(current_user):
    """Submit event suggestion"""
    try:
        data = request.json
        
        suggestion = {
            'userId': current_user,
            'eventTitle': data.get('title'),
            'eventDescription': data.get('description'),
            'category': data.get('category'),
            'status': 'pending',
            'createdAt': datetime.now()
        }
        
        suggestion_ref = db.collection('suggestions').add(suggestion)
        
        return jsonify({
            'success': True,
            'suggestionId': suggestion_ref[1].id,
            'message': 'Suggestion submitted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suggestions_bp.route('/api/suggestions', methods=['GET'])
@require_admin
def get_suggestions(current_user):
    """Get all suggestions (admin only)"""
    try:
        suggestions = []
        for doc in db.collection('suggestions').stream():
            suggestion = doc.to_dict()
            suggestion['id'] = doc.id
            
            # Get user info
            user_doc = db.collection('users').document(suggestion['userId']).get()
            if user_doc.exists:
                suggestion['userName'] = user_doc.to_dict().get('name')
            
            suggestions.append(suggestion)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Utility Files

### Authentication Decorators

```python
# backend/utils/decorators.py
from functools import wraps
from flask import request, jsonify
from services.firebase_service import FirebaseService, db

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        uid = FirebaseService.verify_token(token)
        if not uid:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(uid, *args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        uid = FirebaseService.verify_token(token)
        if not uid:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Check if user is admin
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists or user_doc.to_dict().get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(uid, *args, **kwargs)
    
    return decorated_function
```

### Main App Configuration

```python
# backend/app.py
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # CORS configuration for frontend
    CORS(app, origins=['http://localhost:8080', 'http://localhost:3000'])
    
    # Import blueprints
    from api.auth import auth_bp
    from api.events import events_bp
    from api.bookings import bookings_bp
    from api.profile import profile_bp
    from api.friends import friends_bp
    from api.admin import admin_bp
    from api.suggestions import suggestions_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(suggestions_bp)
    
    @app.route('/')
    def index():
        return {
            'message': 'Nemo API is running!',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth/*',
                'events': '/api/events/*',
                'bookings': '/api/bookings/*',
                'profile': '/api/profile/*',
                'friends': '/api/friends/*',
                'admin': '/api/admin/*',
                'suggestions': '/api/suggestions/*'
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)
```

### Requirements File

```txt
# backend/requirements.txt
Flask==3.0.0
Flask-CORS==4.0.0
firebase-admin==6.1.0
python-dotenv==1.0.0
```

---

## API Documentation for Frontend Team

### Authentication Headers
All protected endpoints require:
```
Authorization: Bearer <firebase_id_token>
```

### Response Format
All responses follow this format:
```json
{
  "success": true/false,
  "data": {...} or "message": "...",
  "error": "..." (if error)
}
```

### Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/auth/register | Register new user | No |
| POST | /api/auth/login