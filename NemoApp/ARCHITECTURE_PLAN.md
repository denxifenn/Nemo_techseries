# Nemo App - MVP Architecture (Backend Focus)

## Project Overview
A community platform for migrant workers in Singapore to discover events, book facilities, form teams, and build social connections.

## Technology Stack (MVP Only)

### Frontend (Handled by Frontend Team)
- **Framework**: Vue.js 3
- **UI Library**: Bootstrap Vue 3 (simpler than Vuetify)
- **State Management**: Pinia
- **Router**: Vue Router 4
- **HTTP Client**: Axios

### Backend (Your Responsibility)
- **Framework**: Flask 3.0
- **API**: RESTful
- **Authentication**: Firebase Auth
- **CORS**: Flask-CORS
- **Environment**: python-dotenv

### Database (Your Responsibility)
- **Primary**: Firebase Firestore (NoSQL)
- **Storage**: Firebase Storage (for images if needed)

### Deployment (MVP)
- **Frontend**: Firebase Hosting (free tier)
- **Backend**: Render.com or Railway (free tier)

## Database Schema (MVP Only)

### Collections Structure

#### 1. users
```javascript
{
  uid: "firebase_auth_uid",
  email: "user@example.com",
  name: "John Doe",
  profilePicture: "https://...",
  role: "user" | "admin",
  friends: ["uid1", "uid2"],
  createdAt: timestamp
}
```

#### 2. events
```javascript
{
  eventId: "auto_generated",
  title: "Football Match",
  description: "Friendly football match...",
  category: "sports" | "workshop" | "social" | "cultural",
  imageUrl: "https://...",
  location: "Kallang Stadium",
  date: "2025-03-15",
  time: "14:00",
  maxParticipants: 20,
  currentParticipants: 12,
  participants: ["uid1", "uid2"],
  createdBy: "admin_uid",
  status: "upcoming" | "completed" | "cancelled",
  createdAt: timestamp
}
```

#### 3. bookings
```javascript
{
  bookingId: "auto_generated",
  eventId: "event_reference",
  userId: "user_uid",
  bookingType: "individual" | "group",
  groupMembers: ["uid1", "uid2"], // if group booking
  status: "confirmed" | "cancelled",
  createdAt: timestamp
}
```

#### 4. friendRequests
```javascript
{
  requestId: "auto_generated",
  fromUserId: "sender_uid",
  toUserId: "receiver_uid",
  status: "pending" | "accepted" | "rejected",
  createdAt: timestamp
}
```

#### 5. suggestions
```javascript
{
  suggestionId: "auto_generated",
  userId: "user_uid",
  text: "Any feedback or suggestions for future events...",
  createdAt: timestamp
}
```

## API Endpoints Structure

### Authentication
- `POST /api/auth/login` - Token verification after frontend Firebase Auth (email/password). Backend never receives passwords.
- `GET /api/auth/verify` - Verify token

### Events
- `GET /api/events` - List all events (with filters)
- `GET /api/events/:id` - Get event details

### Bookings
- `POST /api/bookings/individual` - Individual booking
- `POST /api/bookings/group` - Group booking (supports guest names)
- `GET /api/bookings/my` - Get current user's bookings

### Users
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update profile

### Friends
- `GET /api/friends` - Get friend list
- `POST /api/friends/request` - Send friend request (by email)
- `PUT /api/friends/request/:id` - Accept/reject request

### Suggestions
- `POST /api/suggestions` - Submit suggestion (free-text)
- `GET /api/suggestions` - List suggestions (admin)

## Frontend Components Structure (MVP)

```
src/
├── components/
│   ├── common/
│   │   ├── NavBar.vue
│   │   └── LoadingSpinner.vue
│   ├── events/
│   │   ├── EventCard.vue
│   │   └── EventList.vue
│   ├── bookings/
│   │   ├── IndividualBookingModal.vue
│   │   └── GroupBookingModal.vue
│   └── friends/
│       └── FriendCard.vue
├── views/
│   ├── HomePage.vue
│   ├── LoginPage.vue
│   ├── RegisterPage.vue
│   ├── EventDetailsPage.vue
│   ├── ProfilePage.vue
│   ├── FriendsPage.vue
│   ├── FriendProfilePage.vue
│   ├── CreateEventPage.vue (admin)
│   └── SuggestEventPage.vue
├── router/
│   └── index.js
├── stores/
│   ├── auth.js
│   └── events.js
├── services/
│   ├── api.js
│   └── firebase.js
├── assets/
│   └── styles/
├── App.vue
└── main.js
```

## Backend Structure

```
backend/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── api/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── middleware.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   ├── bookings/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   ├── friends/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   └── admin/
│       ├── __init__.py
│       ├── routes.py
│       └── models.py
├── services/
│   ├── __init__.py
│   ├── firebase_service.py
│   ├── notification_service.py
│   └── validation_service.py
├── utils/
│   ├── __init__.py
│   ├── decorators.py
│   ├── validators.py
│   └── helpers.py
└── tests/
    ├── test_auth.py
    ├── test_events.py
    └── test_bookings.py
```

## Security Considerations (MVP)

1. **Authentication**
   - Firebase Auth for user authentication
   - Token verification for API calls
   - Basic role check (user/admin)

2. **Data Validation**
   - Input validation on backend
   - Firebase security rules

3. **API Security**
   - CORS configuration
   - Environment variables for secrets

## Development Phases (MVP)

### Week 1: Foundation
- Firebase setup (KAN-5, KAN-6)
- Database collections (KAN-27 to KAN-32)
- Authentication APIs (KAN-7)

### Week 2: Core Features
- Events APIs (KAN-8, KAN-9)
- Booking APIs (KAN-10, KAN-11)

### Week 3: Social & Admin
- Profile APIs (KAN-12)
- Friends APIs (KAN-17, KAN-19)
- Admin APIs (KAN-21)
- Suggestions API (KAN-23)

### Week 4: Testing & Deployment
- API testing
- Bug fixes
- Deployment

## MVP Deployment Strategy

1. **Development Environment**
   - Local Flask development server
   - Firebase Emulator Suite for testing

2. **Production Environment (Simple)**
   - Backend on Render.com (free tier)
   - Firebase Firestore (production)
   - Environment variables for configuration

## Testing Strategy

- Postman for API testing
- Unit tests for critical functions
- Manual testing for MVP