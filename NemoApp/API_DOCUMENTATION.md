# Nemo App - API Documentation for Frontend Team

## Base URL
- Development: `http://localhost:5000`
- Production: `TBD (will be provided after deployment)`

## Authentication
Most endpoints require Firebase Authentication. Include the ID token in headers:
```
Authorization: Bearer <firebase_id_token>
```

Note on UIDs and signup/login flow:
- Normal users receive Firebase-generated random, immutable UIDs on registration/sign-in. These are the canonical identifiers used by the backend and Firestore.
- Admin accounts may be provisioned via Firebase Admin SDK with a custom, human-readable UID (e.g., "admin1"). This is optional and performed outside normal user signup.
- Frontend handles email+password sign-in via Firebase Auth to obtain an ID token. The backend never receives raw passwords; it only verifies the ID token and extracts the UID.
## Response Format
All responses follow this structure:
```json
{
  "success": true/false,
  "data": {...} // or specific field names
  "error": "error message" // only on error
}
```

---

## Endpoints

### 1. Authentication

#### Register User
```
POST /api/auth/register
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```
**Response:**
```json
{
  "success": true,
  "uid": "firebase_uid",
  "message": "User registered successfully"
}
```

Notes:
- uid is the Firebase Auth UID. For normal users this is a random alphanumeric string and cannot be changed later.
- Admins can be created via the Firebase Admin SDK with a custom uid if desired; such provisioning is separate from this endpoint.
- After registration, clients should sign in via Firebase Auth (email+password) to obtain an ID token for subsequent API calls. The backend accepts ID tokens and does not handle raw passwords.
#### Login
```
POST /api/auth/login
```
**Body:**
```json
{
  "idToken": "firebase_id_token_from_client_auth"
}
```
**Response:**
```json
{
  "success": true,
  "user": {
    "uid": "user_id",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

#### Verify Token
```
GET /api/auth/verify
Headers: Authorization: Bearer <token>
```
**Response:**
```json
{
  "valid": true,
  "uid": "user_id"
}
```

---

### 2. Events

#### Get All Events
```
GET /api/events
GET /api/events?category=sports
GET /api/events?status=upcoming
```
**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "event_id",
      "title": "Football Match",
      "description": "Friendly match",
      "category": "sports",
      "location": "Kallang Stadium",
      "date": "2025-03-15",
      "time": "14:00",
      "maxParticipants": 20,
      "currentParticipants": 5,
      "status": "upcoming"
    }
  ],
  "count": 1
}
```

#### Get Single Event
```
GET /api/events/{event_id}
```
**Response:**
```json
{
  "success": true,
  "event": {
    "id": "event_id",
    "title": "Football Match",
    "description": "Detailed description...",
    "category": "sports",
    "location": "Kallang Stadium",
    "date": "2025-03-15",
    "time": "14:00",
    "maxParticipants": 20,
    "currentParticipants": 5,
    "participants": ["uid1", "uid2"],
    "createdBy": "admin_uid",
    "status": "upcoming"
  }
}
```

---

### 3. Bookings

#### Create Individual Booking
```
POST /api/bookings/individual
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "eventId": "event_id"
}
```
**Response:**
```json
{
  "success": true,
  "bookingId": "booking_id",
  "message": "Booking confirmed"
}
```

#### Create Group Booking
```
POST /api/bookings/group
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "eventId": "event_id",
  "groupMembers": ["friend_uid1", "friend_uid2"]
}
```
**Response:**
```json
{
  "success": true,
  "bookingId": "booking_id",
  "message": "Group booking confirmed for 3 people"
}
```

#### Get My Bookings
```
GET /api/bookings/my
Headers: Authorization: Bearer <token>
```
**Response:**
```json
{
  "success": true,
  "bookings": [
    {
      "id": "booking_id",
      "eventId": "event_id",
      "bookingType": "individual",
      "status": "confirmed",
      "event": {
        "id": "event_id",
        "title": "Football Match",
        "date": "2025-03-15",
        "time": "14:00"
      }
    }
  ]
}
```

---

### 4. Profile

#### Get Profile
```
GET /api/profile
Headers: Authorization: Bearer <token>
```
**Response:**
```json
{
  "success": true,
  "profile": {
    "uid": "user_id",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "profilePicture": "url_to_image",
    "friends": ["friend_uid1", "friend_uid2"]
  }
}
```

#### Update Profile
```
PUT /api/profile
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "name": "New Name",
  "profilePicture": "new_image_url"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Profile updated"
}
```

---

### 5. Friends

#### Send Friend Request
```
POST /api/friends/request
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "email": "friend@example.com"
}
```
**Response:**
```json
{
  "success": true,
  "requestId": "request_id",
  "message": "Friend request sent"
}
```

#### Accept/Reject Friend Request
```
PUT /api/friends/request/{request_id}
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "action": "accept" // or "reject"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Friend request accepted"
}
```

#### Get Friends List
```
GET /api/friends
Headers: Authorization: Bearer <token>
```
**Response:**
```json
{
  "success": true,
  "friends": [
    {
      "id": "friend_uid",
      "name": "Friend Name",
      "email": "friend@example.com",
      "profilePicture": "image_url"
    }
  ]
}
```

---

### 6. Admin (Admin Role Required)

#### Create Event
```
POST /api/admin/events
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "title": "New Event",
  "description": "Event description",
  "category": "sports",
  "location": "Location",
  "date": "2025-03-20",
  "time": "15:00",
  "maxParticipants": 30,
  "imageUrl": "optional_image_url"
}
```
**Response:**
```json
{
  "success": true,
  "eventId": "new_event_id",
  "message": "Event created successfully"
}
```

---

### 7. Suggestions

#### Submit Suggestion
```
POST /api/suggestions
Headers: Authorization: Bearer <token>
```
**Body:**
```json
{
  "text": "Any feedback or suggestions for future events..."
}
```
**Response:**
```json
{
  "success": true,
  "suggestionId": "suggestion_id",
  "message": "Suggestion submitted successfully"
}
```

#### Get All Suggestions (Admin Only)
```
GET /api/suggestions
Headers: Authorization: Bearer <token>
```
**Response:**
```json
{
  "success": true,
  "suggestions": [
    {
      "id": "suggestion_id",
      "user": {
        "uid": "user_id",
        "name": "John Doe",
        "email": "john@example.com"
      },
      "text": "Any feedback or suggestions for future events...",
      "createdAt": "2025-03-01T13:00:00Z"
    }
  ]
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (missing/invalid data) |
| 401 | Unauthorized (no/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Frontend Integration Example (Vue.js)

### API Service Setup
```javascript
// services/api.js
import axios from 'axios';
import { auth } from './firebase';

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Example API Calls
```javascript
// services/events.js
import api from './api';

export const eventService = {
  // Get all events
  async getEvents(filters = {}) {
    const response = await api.get('/api/events', { params: filters });
    return response.data;
  },

  // Get single event
  async getEvent(eventId) {
    const response = await api.get(`/api/events/${eventId}`);
    return response.data;
  },

  // Book event
  async bookEvent(eventId, groupMembers = null) {
    const endpoint = groupMembers 
      ? '/api/bookings/group' 
      : '/api/bookings/individual';
    
    const data = { eventId };
    if (groupMembers) {
      data.groupMembers = groupMembers;
    }
    
    const response = await api.post(endpoint, data);
    return response.data;
  }
};
```

---

## Testing with Postman

1. **Get Firebase ID Token:**
   - Use Firebase Auth in browser console
   - Get token: `firebase.auth().currentUser.getIdToken()`

2. **Set up Postman:**
   - Create environment variable: `token`
   - Add to headers: `Authorization: Bearer {{token}}`

3. **Test Flow:**
   - Register user
   - Login with token
   - Get events
   - Make booking
   - View profile

---

## Notes for Frontend Team

1. **Authentication Flow:**
   - Use Firebase Auth for client-side authentication
   - Send ID token to backend for verification
   - Store user data in Vuex/Pinia after login

2. **Error Handling:**
   - Always check `success` field in response
   - Display `error` message to user when present
   - Handle 401 errors by redirecting to login

3. **Real-time Updates:**
   - Consider using Firebase listeners for real-time event updates
   - Refresh data after bookings/friend requests

4. **File Uploads:**
   - Profile pictures can be uploaded to Firebase Storage
   - Send the URL to backend after upload

5. **Categories:**
   - Valid categories: `sports`, `workshop`, `social`, `cultural`

6. **Date/Time Format:**
   - Date: "YYYY-MM-DD" (e.g., "2025-03-15")
   - Time: "HH:MM" (24-hour format, e.g., "14:00")

---

## Contact

For backend issues or API questions, contact the backend team.