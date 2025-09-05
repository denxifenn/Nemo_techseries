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
- Frontend handles phone+password sign-in via Firebase Auth using a phone-to-email alias (e.g., 6591234567@phone.local) to obtain an ID token. The backend never receives raw passwords; it only verifies the ID token and extracts the UID.
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

#### Signup (Frontend via Firebase Auth)
- Users sign up in the frontend using Firebase Auth (phone+password via phone-to-email alias). The backend never receives raw passwords.
- Firebase issues an immutable UID per user (random alphanumeric string).
- Admin/service accounts can still be provisioned via the Firebase Admin SDK out-of-band if needed.
#### Login
```
POST /api/auth/login
```
**Body:**
```json
{
  "idToken": "firebase_id_token_from_client_auth",
  "phoneNumber": "+6591234567",
  "name": "John Doe"
}
```
Notes:
- phoneNumber and name are optional and used to enrich the Firestore user document on first login.
- phoneNumber should be E.164 formatted (+65XXXXXXXX).

**Response:**
```json
{
  "success": true,
  "user": {
    "uid": "user_id",
    "phoneNumber": "+6591234567",
    "fullName": "John Doe",
    "name": "John Doe",
    "role": "user"
  }
}
```
Notes:
- On first successful login, the backend auto-creates the user's Firestore profile document if it does not already exist.

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
GET /api/events?limit=20
```
Note:
- Optional query parameters: category, status, limit (default 20, max 50).
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
**Body (supports both):**
```json
{
  "eventId": "event_id",
  "groupMembers": ["friend_uid1", "friend_uid2"],
  "groupMemberNames": ["Alice", "Bob"]
}
```
Notes:
- Only the initiating user's UID is counted; any provided groupMembers UIDs are ignored by the backend (initiator-only UID policy).
- Use groupMemberNames to include additional attendees without accounts.
- Capacity is enforced atomically across the initiator seat (if newly added) and guest names.
- Guest names are stored on the event as guestEntries and on the booking as guestNames.

**Response:**
```json
{
  "success": true,
  "bookingId": "booking_id",
  "joinedCount": 3,
  "message": "Group booking confirmed for 3 member(s) added"
}
```

#### Get My Bookings
```
GET /api/bookings/my
Headers: Authorization: Bearer <token>
```
Optional query:
- filter=current|past|all (default current)
  - current: upcoming events (start >= now) and not cancelled
  - past: events already started (start < now) OR cancelled bookings
  - all: no filtering

Examples:
- GET /api/bookings/my?filter=current
- GET /api/bookings/my?filter=past
- GET /api/bookings/my?filter=all

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
  ],
  "count": 1
}
```

#### Cancel My Booking
```
DELETE /api/bookings/{booking_id}
Headers: Authorization: Bearer <token>
```
Rules:
- Only the booking owner (userId) can cancel
- Booking must be in status=confirmed
- Cannot cancel within 24 hours before the event start time

**Response:**
```json
{
  "success": true,
  "message": "Booking cancelled",
  "seatsFreed": 2
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
    "phoneNumber": "+6591234567",
    "fullName": "John Doe",
    "age": 28,
    "nationality": "Singaporean",
    "languages": ["English", "Mandarin"],
    "homeCountry": "Singapore",
    "restDays": ["Saturday", "Sunday"],
    "interests": ["Football", "Cooking"],
    "skills": [
      {"name": "Programming", "rating": "Expert"},
      {"name": "Cooking", "rating": "Proficient"}
    ],
    "role": "user",
    "profilePicture": "url_to_image",
    "friends": ["friend_uid1", "friend_uid2"],
    "profileCompleted": true,
    "profileCompletedAt": "2025-03-01T10:00:00Z",
    "createdAt": "2025-02-28T10:00:00Z",
    "updatedAt": "2025-03-01T10:00:00Z"
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
  "fullName": "New Name",
  "age": 28,
  "nationality": "Singaporean",
  "languages": ["English", "Mandarin"],
  "homeCountry": "Singapore",
  "restDays": ["Saturday", "Sunday"],
  "interests": ["Football", "Cooking"],
  "skills": [
    {"name": "Web Development", "rating": "Expert"},
    {"name": "Photography", "rating": "Basic"}
  ],
  "profilePicture": "new_image_url"
}
```
Validation:
- fullName: 1-100 chars
- age: integer 18-100
- nationality: non-empty string (2-50 chars)
- languages: array with at least 1 language (each 2-30 chars, max 10)
- homeCountry: non-empty string (2-50 chars)
- restDays: array of weekdays (["Monday".."Sunday"])
- interests: array of strings (max 20, each 1-50 chars)
- skills: array of { name: 1-50 chars, rating: "Basic" | "Proficient" | "Expert" } (max 20)

**Response:**
```json
{
  "success": true,
  "message": "Profile updated",
  "updated": {
    "fullName": "New Name",
    "age": 28,
    "nationality": "Singaporean",
    "languages": ["English", "Mandarin"],
    "homeCountry": "Singapore",
    "restDays": ["Saturday", "Sunday"],
    "interests": ["Football", "Cooking"],
    "skills": [
      {"name": "Web Development", "rating": "Expert"},
      {"name": "Photography", "rating": "Basic"}
    ],
    "profilePicture": "new_image_url"
  },
  "profileCompleted": true,
  "missingFields": []
}
```

#### Profile Completion Status
```
GET /api/profile/completion-status
Headers: Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "status": {
    "profileCompleted": false,
    "missingFields": ["age", "nationality", "languages"],
    "completedFields": ["fullName", "phoneNumber", "homeCountry", "restDays"],
    "totalRequired": 7,
    "totalCompleted": 4,
    "completionPercentage": 57
  }
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
  "phoneNumber": "+6591234567"
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
      "phoneNumber": "+6591234567",
      "profilePicture": "image_url"
    }
  ],
  "count": 1
}
```

---

### 6. Admin (Admin Role Required)

#### Health Check
```
GET /api/admin/health
Headers: Authorization: Bearer <token>
```
**Response:**
```json
{
  "success": true,
  "user": "admin_uid",
  "message": "Admin routes available"
}
```

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

Validation:
- Event start must be in the future (creation is rejected if date/time is in the past)

#### Update Event
```
PUT /api/admin/events/{event_id}
Headers: Authorization: Bearer <token>
```
Body (any subset):
```json
{
  "title": "New Title",
  "description": "Updated description",
  "category": "sports|workshop|social|cultural",
  "location": "New Location",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "maxParticipants": 50,
  "imageUrl": "optional_image_url"
}
```
Rules:
- category, if provided, must be one of: sports, workshop, social, cultural
- date/time, if provided, must not result in a past scheduled time
- maxParticipants, if provided, must be >= currentParticipants

**Response:**
```json
{
  "success": true,
  "message": "Event updated",
  "updated": {
    "title": "New Title",
    "time": "16:00"
  }
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
  "message": "Suggestion submitted"
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
        "phoneNumber": "+6591234567"
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