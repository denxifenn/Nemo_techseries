# Jira Tasks - Detailed Implementation Guide

## Task Breakdown with Code Examples

### Foundation Tasks

#### KAN-5: Research about Firebase
**Status**: Documentation
**Description**: Understanding Firebase services needed for the project

**Key Points**:
1. Firebase Authentication for user management
2. Firestore for NoSQL database
3. Firebase Storage for images
4. Firebase Hosting for frontend deployment

#### KAN-6: Integrate Firebase with Backend
**Implementation**:

```python
# backend/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

def initialize_firebase():
    cred = credentials.Certificate('firebase/firebase-admin-key.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = initialize_firebase()
```

### Database Collections Tasks

#### KAN-27: Create Users Collection
```javascript
// Firestore Structure
users/{userId}
{
  uid: "auto_generated",
  email: "user@example.com",
  name: "John Doe",
  role: "user", // or "admin"
  profilePicture: "",
  friends: [],
  createdAt: timestamp
}
```

#### KAN-28: Create Events Collection
```javascript
events/{eventId}
{
  eventId: "auto_generated",
  title: "Football Match",
  description: "Join us for a friendly match",
  category: "sports",
  imageUrl: "",
  location: "Kallang Stadium",
  date: "2025-03-15",
  time: "14:00",
  maxParticipants: 20,
  currentParticipants: 0,
  participants: [], // array of user IDs
  createdBy: "admin_uid",
  createdAt: timestamp
}
```

#### KAN-29: Create Bookings Collection
```javascript
bookings/{bookingId}
{
  bookingId: "auto_generated",
  eventId: "event_ref",
  userId: "user_ref",
  bookingType: "individual", // or "group"
  groupMembers: [], // if group booking
  status: "confirmed",
  createdAt: timestamp
}
```

#### KAN-30: Create Friend_Requests Collection
```javascript
friendRequests/{requestId}
{
  requestId: "auto_generated",
  fromUserId: "sender_uid",
  toUserId: "receiver_uid",
  status: "pending", // "accepted", "rejected"
  createdAt: timestamp
}
```

#### KAN-31: Create Suggestions Collection
```javascript
suggestions/{suggestionId}
{
  suggestionId: "auto_generated",
  userId: "user_uid",
  eventTitle: "Cooking Workshop",
  eventDescription: "Learn local cuisine",
  category: "workshop",
  status: "pending", // "approved", "rejected"
  createdAt: timestamp
}
```

#### KAN-32: Create Admin Collection
```javascript
admins/{adminId}
{
  adminId: "auto_generated",
  userId: "user_ref",
  permissions: ["create_event", "manage_users", "view_suggestions"],
  createdAt: timestamp
}
```

### Authentication Tasks

#### KAN-7: Create Login Function + API
**Backend Implementation**:
```python
# backend/api/auth.py
from flask import Blueprint, request, jsonify
from services.firebase_service import auth, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Firebase handles authentication
    # Return token to frontend
    return jsonify({"message": "Login endpoint", "email": email})

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    # Create user in Firebase Auth
    # Add user details to Firestore
    return jsonify({"message": "Register endpoint"})
```

#### KAN-14: Login Page
**Frontend Implementation**:
```vue
<!-- frontend/src/views/LoginPage.vue -->
<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="email" type="email" placeholder="Email" required>
      <input v-model="password" type="password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>
    <router-link to="/register">Don't have an account? Register</router-link>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser } from '@/services/auth'

export default {
  setup() {
    const email = ref('')
    const password = ref('')
    const router = useRouter()
    
    const handleLogin = async () => {
      try {
        await loginUser(email.value, password.value)
        router.push('/home')
      } catch (error) {
        console.error('Login failed:', error)
      }
    }
    
    return { email, password, handleLogin }
  }
}
</script>
```

#### KAN-15: Register Page
```vue
<!-- frontend/src/views/RegisterPage.vue -->
<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <input v-model="name" type="text" placeholder="Full Name" required>
      <input v-model="email" type="email" placeholder="Email" required>
      <input v-model="password" type="password" placeholder="Password" required>
      <button type="submit">Register</button>
    </form>
  </div>
</template>
```

### Events Tasks

#### KAN-4: Events Page
```vue
<!-- frontend/src/views/EventsPage.vue -->
<template>
  <div class="events-page">
    <h1>Upcoming Events</h1>
    <div class="filters">
      <button @click="filterBy('all')">All</button>
      <button @click="filterBy('sports')">Sports</button>
      <button @click="filterBy('workshop')">Workshops</button>
      <button @click="filterBy('social')">Social</button>
    </div>
    <div class="events-grid">
      <EventCard v-for="event in filteredEvents" :key="event.id" :event="event" />
    </div>
  </div>
</template>
```

#### KAN-8: Create View Events on Homepage + API
**Backend**:
```python
# backend/api/events.py
@events_bp.route('/api/events', methods=['GET'])
def get_events():
    events_ref = db.collection('events')
    events = []
    for doc in events_ref.stream():
        event = doc.to_dict()
        event['id'] = doc.id
        events.append(event)
    return jsonify(events)
```

#### KAN-13: Events Details Page
```vue
<!-- frontend/src/views/EventDetailsPage.vue -->
<template>
  <div class="event-details">
    <img :src="event.imageUrl" :alt="event.title">
    <h1>{{ event.title }}</h1>
    <p>{{ event.description }}</p>
    <div class="event-info">
      <p>📍 {{ event.location }}</p>
      <p>📅 {{ event.date }}</p>
      <p>⏰ {{ event.time }}</p>
      <p>👥 {{ event.currentParticipants }}/{{ event.maxParticipants }} participants</p>
    </div>
    <button @click="openBookingModal">Book Now</button>
  </div>
</template>
```

### Booking Tasks

#### KAN-9: Create View Single Event After Clicking + API
**Backend**:
```python
@events_bp.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    event_ref = db.collection('events').document(event_id)
    event = event_ref.get()
    if event.exists:
        return jsonify(event.to_dict())
    return jsonify({"error": "Event not found"}), 404
```

#### KAN-16: Individual Registration Pop-up
```vue
<!-- frontend/src/components/IndividualBookingModal.vue -->
<template>
  <div class="modal" v-if="show">
    <div class="modal-content">
      <h3>Book Event - Individual</h3>
      <p>Event: {{ event.title }}</p>
      <p>Date: {{ event.date }}</p>
      <button @click="confirmBooking">Confirm Booking</button>
      <button @click="$emit('close')">Cancel</button>
    </div>
  </div>
</template>
```

#### KAN-10: Create Book by Yourself Confirmation + API
**Backend**:
```python
@bookings_bp.route('/api/bookings/individual', methods=['POST'])
def create_individual_booking():
    data = request.json
    booking = {
        'eventId': data['eventId'],
        'userId': data['userId'],
        'bookingType': 'individual',
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    db.collection('bookings').add(booking)
    return jsonify({"message": "Booking confirmed"})
```

#### KAN-18: Group Registration Pop-up
```vue
<!-- frontend/src/components/GroupBookingModal.vue -->
<template>
  <div class="modal" v-if="show">
    <div class="modal-content">
      <h3>Book Event - Group</h3>
      <p>Select friends to invite:</p>
      <div v-for="friend in friends" :key="friend.id">
        <input type="checkbox" :value="friend.id" v-model="selectedFriends">
        <label>{{ friend.name }}</label>
      </div>
      <button @click="confirmGroupBooking">Confirm Group Booking</button>
    </div>
  </div>
</template>
```

#### KAN-11: Create Book with Friends Confirmation + API
**Backend**:
```python
@bookings_bp.route('/api/bookings/group', methods=['POST'])
def create_group_booking():
    data = request.json
    booking = {
        'eventId': data['eventId'],
        'userId': data['userId'],
        'bookingType': 'group',
        'groupMembers': data['groupMembers'],
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    db.collection('bookings').add(booking)
    return jsonify({"message": "Group booking confirmed"})
```

### Profile Tasks

#### KAN-12: Create Profile Page (View/Edit) + API
**Backend**:
```python
@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    user_id = request.args.get('userId')
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        return jsonify(user.to_dict())
    return jsonify({"error": "User not found"}), 404

@profile_bp.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.json
    user_id = data['userId']
    updates = {
        'name': data.get('name'),
        'profilePicture': data.get('profilePicture')
    }
    db.collection('users').document(user_id).update(updates)
    return jsonify({"message": "Profile updated"})
```

#### KAN-24: Profile Page
```vue
<!-- frontend/src/views/ProfilePage.vue -->
<template>
  <div class="profile-page">
    <h2>My Profile</h2>
    <div class="profile-info">
      <img :src="user.profilePicture || defaultAvatar" alt="Profile">
      <div v-if="!editing">
        <h3>{{ user.name }}</h3>
        <p>{{ user.email }}</p>
        <button @click="editing = true">Edit Profile</button>
      </div>
      <div v-else>
        <input v-model="user.name" placeholder="Name">
        <button @click="saveProfile">Save</button>
        <button @click="editing = false">Cancel</button>
      </div>
    </div>
  </div>
</template>
```

### Friends Tasks

#### KAN-17: Create Adding Friend Function + API
**Backend**:
```python
@friends_bp.route('/api/friends/request', methods=['POST'])
def send_friend_request():
    data = request.json
    request_data = {
        'fromUserId': data['fromUserId'],
        'toUserId': data['toUserId'],
        'status': 'pending',
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    db.collection('friendRequests').add(request_data)
    return jsonify({"message": "Friend request sent"})
```

#### KAN-19: Create View Friends Function + API
**Backend**:
```python
@friends_bp.route('/api/friends', methods=['GET'])
def get_friends():
    user_id = request.args.get('userId')
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        friends = user.to_dict().get('friends', [])
        return jsonify(friends)
    return jsonify([])
```

#### KAN-25: My Friends Page
```vue
<!-- frontend/src/views/FriendsPage.vue -->
<template>
  <div class="friends-page">
    <h2>My Friends</h2>
    <div class="add-friend">
      <input v-model="friendEmail" placeholder="Enter friend's email">
      <button @click="sendFriendRequest">Add Friend</button>
    </div>
    <div class="friends-list">
      <div v-for="friend in friends" :key="friend.id" class="friend-card">
        <img :src="friend.profilePicture" :alt="friend.name">
        <h4>{{ friend.name }}</h4>
        <router-link :to="`/friend/${friend.id}`">View Profile</router-link>
      </div>
    </div>
  </div>
</template>
```

#### KAN-26: My Friend's Profile Page
```vue
<!-- frontend/src/views/FriendProfilePage.vue -->
<template>
  <div class="friend-profile">
    <h2>{{ friend.name }}'s Profile</h2>
    <img :src="friend.profilePicture" :alt="friend.name">
    <p>Member since: {{ friend.createdAt }}</p>
    <h3>Upcoming Events</h3>
    <div v-for="event in friendEvents" :key="event.id">
      <p>{{ event.title }} - {{ event.date }}</p>
    </div>
  </div>
</template>
```

### Admin Tasks

#### KAN-21: Create Admin Create Event Page Function + API
**Backend**:
```python
@admin_bp.route('/api/admin/events', methods=['POST'])
def create_event():
    # Check if user is admin
    data = request.json
    event = {
        'title': data['title'],
        'description': data['description'],
        'category': data['category'],
        'location': data['location'],
        'date': data['date'],
        'time': data['time'],
        'maxParticipants': data['maxParticipants'],
        'currentParticipants': 0,
        'createdBy': data['userId'],
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    db.collection('events').add(event)
    return jsonify({"message": "Event created successfully"})
```

#### KAN-22: Create An Event Page (Admin)
```vue
<!-- frontend/src/views/CreateEventPage.vue -->
<template>
  <div class="create-event">
    <h2>Create New Event</h2>
    <form @submit.prevent="createEvent">
      <input v-model="event.title" placeholder="Event Title" required>
      <textarea v-model="event.description" placeholder="Description" required></textarea>
      <select v-model="event.category">
        <option value="sports">Sports</option>
        <option value="workshop">Workshop</option>
        <option value="social">Social</option>
      </select>
      <input v-model="event.location" placeholder="Location" required>
      <input v-model="event.date" type="date" required>
      <input v-model="event.time" type="time" required>
      <input v-model="event.maxParticipants" type="number" placeholder="Max Participants" required>
      <button type="submit">Create Event</button>
    </form>
  </div>
</template>
```

### Suggestions Tasks

#### KAN-20: Suggest An Event Page (Normal User)
```vue
<!-- frontend/src/views/SuggestEventPage.vue -->
<template>
  <div class="suggest-event">
    <h2>Suggest an Event</h2>
    <form @submit.prevent="submitSuggestion">
      <input v-model="suggestion.title" placeholder="Event Title" required>
      <textarea v-model="suggestion.description" placeholder="Describe your event idea" required></textarea>
      <select v-model="suggestion.category">
        <option value="sports">Sports</option>
        <option value="workshop">Workshop</option>
        <option value="social">Social</option>
      </select>
      <button type="submit">Submit Suggestion</button>
    </form>
  </div>
</template>
```

#### KAN-23: Create Leave Your Suggestions Below + API
**Backend**:
```python
@suggestions_bp.route('/api/suggestions', methods=['POST'])
def create_suggestion():
    data = request.json
    suggestion = {
        'userId': data['userId'],
        'eventTitle': data['title'],
        'eventDescription': data['description'],
        'category': data['category'],
        'status': 'pending',
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    db.collection('suggestions').add(suggestion)
    return jsonify({"message": "Suggestion submitted successfully"})

@suggestions_bp.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    # Admin only endpoint
    suggestions = []
    for doc in db.collection('suggestions').stream():
        suggestion = doc.to_dict()
        suggestion['id'] = doc.id
        suggestions.append(suggestion)
    return jsonify(suggestions)
```
## Ignored at the moment
## Implementation Priority Order

### Phase 1: Foundation (Days 1-3)
- [x] KAN-5: Research Firebase
- [ ] KAN-6: Firebase integration
- [ ] KAN-27-32: Create all collections

### Phase 2: Authentication (Days 4-5)
- [ ] KAN-7: Login API
- [ ] KAN-14: Login page
- [ ] KAN-15: Register page

### Phase 3: Events Core (Days 6-8)
- [ ] KAN-8: Events API
- [ ] KAN-4: Events page
- [ ] KAN-9: Single event API
- [ ] KAN-13: Event details page

### Phase 4: Bookings (Days 9-11)
- [ ] KAN-10: Individual booking API
- [ ] KAN-16: Individual booking modal
- [ ] KAN-11: Group booking API
- [ ] KAN-18: Group booking modal

### Phase 5: Profile & Friends (Days 12-14)
- [ ] KAN-12: Profile API
- [ ] KAN-24: Profile page
- [ ] KAN-17: Add friend API
- [ ] KAN-19: View friends API
- [ ] KAN-25: Friends page
- [ ] KAN-26: Friend profile page

### Phase 6: Admin & Suggestions (Days 15-16)
- [ ] KAN-21: Admin event API
- [ ] KAN-22: Create event page
- [ ] KAN-23: Suggestions API
- [ ] KAN-20: Suggest event page

### Phase 7: Testing & Deployment (Days 17-18)
- [ ] Integration testing
- [ ] Bug fixes
- [ ] Deployment

## Notes
- Each task includes both frontend and backend components
- APIs should be tested with Postman before frontend integration
- Use Firebase emulator for local development
- Implement basic error handling for all API endpoints
- Add loading states for all async operations in frontend