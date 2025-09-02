# Nemo App - MVP Implementation Plan

## Scope Clarification
This plan focuses ONLY on MVP features from the Jira tasks. We are NOT implementing:
- FWMOMCare authentication integration (future)
- Waitlist and queueing system (future)
- Gamification features (future)
- Advanced social networking beyond basic friends (future)
- Offline mode (future)
- Multilingual support beyond basic structure (future - keep simple for MVP)

## MVP Feature Set (Based on Jira Tasks)

### Core Features to Implement

#### 1. Authentication (KAN-7, KAN-14, KAN-15)
- Simple email/password login using Firebase Auth
- Basic registration page
- Session management

#### 2. Events System (KAN-4, KAN-8, KAN-13)
- Homepage with events list
- Event details page
- Browse events functionality
- Simple filtering by category

#### 3. Booking System (KAN-9, KAN-10, KAN-11, KAN-16, KAN-18)
- Individual event registration
- Group/team registration
- Booking confirmation system
- View my bookings

#### 4. User Profile (KAN-12, KAN-24)
- View profile page
- Edit profile functionality
- Basic user information

#### 5. Friends System (KAN-17, KAN-19, KAN-25, KAN-26)
- Add friend functionality
- View friends list
- View friend's profile
- Send friend requests

#### 6. Admin Features (KAN-21, KAN-22)
- Admin create event page
- Basic admin panel
- Manage events

#### 7. Suggestions (KAN-20, KAN-23)
- User can suggest events
- Simple suggestion form
- Admin can view suggestions

## Simplified Database Schema for MVP

### Collections (Firebase Firestore)

#### users (KAN-27)
```javascript
{
  uid: "firebase_auth_uid",
  email: "user@example.com",
  name: "John Doe",
  role: "user" | "admin",
  profilePicture: "url_to_image",
  createdAt: timestamp
}
```

#### events (KAN-28)
```javascript
{
  eventId: "auto_generated",
  title: "Football Match",
  description: "Friendly football match at Kallang",
  category: "sports",
  imageUrl: "https://...",
  location: "Kallang Stadium",
  date: "2025-03-15",
  time: "14:00",
  maxParticipants: 20,
  currentParticipants: 0,
  createdBy: "admin_uid",
  createdAt: timestamp
}
```

#### bookings (KAN-29)
```javascript
{
  bookingId: "auto_generated",
  eventId: "event_reference",
  userId: "user_uid",
  bookingType: "individual" | "group",
  groupMembers: [], // array of user IDs if group booking
  createdAt: timestamp
}
```

#### friendRequests (KAN-30)
```javascript
{
  requestId: "auto_generated",
  fromUserId: "sender_uid",
  toUserId: "receiver_uid",
  status: "pending" | "accepted" | "rejected",
  createdAt: timestamp
}
```

#### suggestions (KAN-31)
```javascript
{
  suggestionId: "auto_generated",
  userId: "user_uid",
  eventTitle: "Cooking Class",
  eventDescription: "Learn to cook local dishes",
  createdAt: timestamp
}
```

## Simplified API Endpoints for MVP

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Events
- `GET /api/events` - List all events
- `GET /api/events/{id}` - Get single event
- `POST /api/events` - Create event (admin only)

### Bookings
- `POST /api/bookings/individual` - Individual booking
- `POST /api/bookings/group` - Group booking
- `GET /api/bookings/my` - Get user's bookings

### Profile
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update profile

### Friends
- `GET /api/friends` - Get friends list
- `POST /api/friends/request` - Send friend request
- `PUT /api/friends/request/{id}` - Accept/reject request
- `GET /api/friends/{id}` - View friend profile

### Suggestions
- `POST /api/suggestions` - Submit suggestion
- `GET /api/suggestions` - Get all suggestions (admin)

### Admin
- `POST /api/admin/events` - Create event
- `GET /api/admin/suggestions` - View suggestions

## Frontend Pages Structure (Based on Jira)

```
Pages:
├── Login Page (KAN-14)
├── Register Page (KAN-15)
├── Home/Events Page (KAN-4, KAN-8)
├── Event Details Page (KAN-13)
│   ├── Individual Registration Modal (KAN-16)
│   └── Group Registration Modal (KAN-18)
├── Profile Page (KAN-24)
├── My Friends Page (KAN-25)
├── Friend's Profile Page (KAN-26)
├── Suggest Event Page (KAN-20)
└── Admin Pages
    └── Create Event Page (KAN-22)
```

## Implementation Order (Aligned with Dependencies)

### Week 1: Foundation
1. **KAN-5**: Research Firebase setup
2. **KAN-6**: Integrate Firebase with backend
3. **KAN-27**: Create users collection
4. **KAN-28**: Create events collection
5. **KAN-7**: Create login function + API

### Week 2: Core Features
1. **KAN-14**: Login page
2. **KAN-15**: Register page
3. **KAN-4**: Events page
4. **KAN-8**: View events on homepage + API
5. **KAN-13**: Event details page

### Week 3: Booking System
1. **KAN-29**: Create bookings collection
2. **KAN-9**: View single event + API
3. **KAN-16**: Individual registration popup
4. **KAN-10**: Book by yourself confirmation + API
5. **KAN-18**: Group registration popup
6. **KAN-11**: Book with friends confirmation + API

### Week 4: Social Features
1. **KAN-30**: Create friend_requests collection
2. **KAN-12**: Profile page (view/edit) + API
3. **KAN-24**: Profile page implementation
4. **KAN-17**: Add friend function + API
5. **KAN-19**: View friends function + API
6. **KAN-25**: My Friends page
7. **KAN-26**: Friend's Profile page

### Week 5: Admin & Final Features
1. **KAN-32**: Create Admin collection
2. **KAN-21**: Admin create event function + API
3. **KAN-22**: Create event page (admin)
4. **KAN-31**: Create suggestions collection
5. **KAN-23**: Leave suggestions + API
6. **KAN-20**: Suggest event page

## Technical Decisions for MVP

### Frontend
- **Vue 3** with Composition API
- **Vue Router** for navigation
- **Pinia** for state management (simpler than Vuex)
- **Bootstrap Vue 3** for quick UI development
- **Axios** for API calls

### Backend
- **Flask** with blueprints for organization
- **Flask-CORS** for cross-origin requests
- **Firebase Admin SDK** for Firestore access
- **Flask-RESTful** for API structure

### Deployment (Simple MVP)
- **Frontend**: Firebase Hosting (free tier)
- **Backend**: Render.com or Railway (free tier)
- **Database**: Firebase Firestore (free tier)

## File Structure for MVP

### Frontend
```
frontend/src/
├── components/
│   ├── EventCard.vue
│   ├── EventList.vue
│   ├── BookingModal.vue
│   ├── FriendCard.vue
│   └── NavBar.vue
├── views/
│   ├── LoginPage.vue
│   ├── RegisterPage.vue
│   ├── HomePage.vue
│   ├── EventDetailsPage.vue
│   ├── ProfilePage.vue
│   ├── FriendsPage.vue
│   ├── FriendProfilePage.vue
│   ├── SuggestEventPage.vue
│   └── CreateEventPage.vue
├── services/
│   ├── api.js
│   └── auth.js
├── router/
│   └── index.js
├── stores/
│   ├── auth.js
│   └── events.js
└── main.js
```

### Backend
```
backend/
├── app.py
├── config.py
├── requirements.txt
├── api/
│   ├── auth.py
│   ├── events.py
│   ├── bookings.py
│   ├── profile.py
│   ├── friends.py
│   ├── suggestions.py
│   └── admin.py
├── services/
│   └── firebase_service.py
└── utils/
    └── decorators.py
```

## MVP Success Criteria

1. Users can register and login
2. Users can browse events
3. Users can book events (individually or as a group)
4. Users can manage their profile
5. Users can add friends and view friend profiles
6. Users can suggest new events
7. Admins can create events
8. Basic responsive design for mobile

## What We're NOT Building (Yet)

- Complex authentication (FWMOMCare integration)
- Payment processing
- Email/SMS notifications
- Advanced search and filters
- Waitlists
- Gamification/points system
- Offline functionality
- Full multilingual support (just English for MVP)
- Analytics dashboard
- Complex admin panel

## Next Steps

1. Set up Firebase project
2. Initialize Vue.js and Flask projects with basic structure
3. Implement authentication flow
4. Build event listing and details
5. Add booking functionality
6. Implement friends system
7. Add admin features
8. Deploy MVP

This focused approach ensures we deliver a working MVP that covers all Jira tasks without scope creep from future features.