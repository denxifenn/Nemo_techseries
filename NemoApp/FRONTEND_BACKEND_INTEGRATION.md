# Frontend-Backend Integration Guide

## Overview
This document provides a comprehensive guide for integrating the NemoApp frontend (Vue.js) with the backend (Flask + Firebase). It includes all critical information, API endpoints, schema definitions, and implementation requirements.

## Table of Contents
1. [Authentication System](#authentication-system)
2. [User Profile Requirements](#user-profile-requirements)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Data Schema Alignment](#data-schema-alignment)
5. [Implementation Tasks](#implementation-tasks)
6. [Critical Issues & Solutions](#critical-issues--solutions)

---

## Authentication System

### Phone Number Authentication
- **Method**: Phone numbers converted to email aliases for Firebase Auth
- **Format**: `6591234567@phone.local` (without + sign in email)
- **Singapore Format**: Accept 8-digit numbers, auto-prepend +65

### Login Flow
1. User enters phone number (e.g., "91234567") and password
2. Frontend formats to "+6591234567"
3. Converts to email: "6591234567@phone.local"
4. Firebase Auth with email/password
5. Get ID token and send to backend `/api/auth/login`
6. Backend verifies token and returns user data

### Required Fields for Signup
- Phone Number (8 digits, Singapore)
- Password
- First Name
- Last Name
- **FIN Number** (NEW - needs backend implementation)

---

## User Profile Requirements

### Required Fields (Must Complete After First Login)
1. `fullName` - string (1-100 characters)
2. `age` - number (18-100)
3. `nationality` - string (e.g., "Singaporean")
4. `languages` - array (at least 1 language)
5. `homeCountry` - string
6. `restDays` - array of weekdays
7. `phoneNumber` - automatically set from signup
8. **`finNumber`** - string (NEW - to be added)

### Optional Fields
- `interests` - array of strings (max 20)
- `skills` - array of {name, rating: "Basic"|"Proficient"|"Expert"}
- `profilePicture` - URL string

### Profile Completion Flow
1. After first login, check `/api/profile/completion-status`
2. If `profileCompleted: false`, redirect to ProfileCompletion.vue
3. Block all other navigation until profile is complete
4. Once complete, allow full site access

---

## API Endpoints Reference

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | Login with ID token | No |
| GET | `/api/auth/verify` | Verify token validity | Yes |

### Events
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/events` | List all events with filters | No |
| GET | `/api/events/{id}` | Get single event details | No |
| POST | `/api/admin/events` | Create new event | Admin only |
| PUT | `/api/admin/events/{id}` | Update event | Admin only |

#### Event Filters (Query Parameters)
- `format`: online|offline
- `type`: sports|arts|culture|music|performance|workshop|tours|other
- `region`: north|south|east|west|central
- `timing`: morning|afternoon|evening|night
- `fromDate`: YYYY-MM-DD
- `toDate`: YYYY-MM-DD
- `minPrice`: number
- `maxPrice`: number
- `status`: upcoming|completed|cancelled
- `limit`: max 50 (default 20)

### Bookings
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/bookings/individual` | Individual booking | Yes |
| POST | `/api/bookings/group` | Group booking | Yes |
| GET | `/api/bookings/my` | Get user's bookings | Yes |
| DELETE | `/api/bookings/{id}` | Cancel booking | Yes |

### Profile
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/profile` | Get current user profile | Yes |
| PUT | `/api/profile` | Update profile | Yes |
| GET | `/api/profile/completion-status` | Check if profile complete | Yes |

### Friends
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/friends` | Get friends list | Yes |
| POST | `/api/friends/request` | Send friend request | Yes |
| PUT | `/api/friends/request/{id}` | Accept/reject request | Yes |

### Suggestions
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/suggestions` | Submit suggestion | Yes |
| GET | `/api/suggestions` | Get all suggestions | Admin only |

---

## Data Schema Alignment

### Event Schema (Backend → Frontend)
```javascript
{
  id: "event_id",
  title: "Event Title",
  description: "Event description",
  format: "offline",              // "online" | "offline"
  venueType: "indoor",            // "indoor" | "outdoor" (only if offline)
  type: "sports",                 // sports|arts|culture|music|performance|workshop|tours|other
  region: "north",                // north|south|east|west|central (Singapore regions)
  organiser: "Organiser Name",
  location: "Event Location",
  date: "2025-03-15",            // YYYY-MM-DD
  startTime: "14:00",            // HH:MM (24-hour)
  endTime: "16:00",              // HH:MM (24-hour)
  timing: "afternoon",           // Derived: morning|afternoon|evening|night
  price: 0,                      // SGD
  imageUrl: "https://...",       // Optional
  maxParticipants: 50,
  currentParticipants: 10,
  availableSlots: 40,            // Computed: max - current
  participants: ["uid1", "uid2"],
  status: "upcoming"             // upcoming|completed|cancelled
}
```

### User Schema (with FIN addition)
```javascript
{
  uid: "firebase_uid",
  phoneNumber: "+6591234567",
  fullName: "John Doe",
  finNumber: "S1234567A",        // NEW FIELD
  age: 28,
  nationality: "Singaporean",
  languages: ["English", "Mandarin"],
  homeCountry: "Singapore",
  restDays: ["Saturday", "Sunday"],
  interests: ["Football", "Cooking"],
  skills: [
    {name: "Programming", rating: "Expert"},
    {name: "Cooking", rating: "Proficient"}
  ],
  role: "user",                  // "user" | "admin"
  profilePicture: "url",
  friends: ["uid1", "uid2"],
  profileCompleted: true,
  profileCompletedAt: timestamp,
  createdAt: timestamp,
  updatedAt: timestamp
}
```

---

## Implementation Tasks

### Priority 1: Core Setup
- [ ] Install Pinia: `npm install pinia`
- [ ] Create auth store with user state management
- [ ] Add FIN field to backend user schema
- [ ] Update Firebase service to handle FIN

### Priority 2: Authentication & Profile
- [ ] Remove email references from UI
- [ ] Create ProfileCompletion.vue component
- [ ] Implement profile completion guard
- [ ] Add logout functionality

### Priority 3: Navigation & Access Control
- [ ] Remove API tester from NavBar
- [ ] Implement conditional rendering based on auth state
- [ ] Hide "Create Event" for non-admin users
- [ ] Add "Sign In" only when not logged in

### Priority 4: Event Integration
- [ ] Fix EventCreation.vue region values:
  ```javascript
  // WRONG (current)
  { label: "North", value: "north-america" }
  
  // CORRECT (Singapore regions)
  { label: "North", value: "north" },
  { label: "South", value: "south" },
  { label: "East", value: "east" },
  { label: "West", value: "west" },
  { label: "Central", value: "central" }
  ```
- [ ] Connect Discover page to backend API
- [ ] Implement event filtering
- [ ] Add placeholder images for missing imageUrl
- [ ] Connect Event detail page to backend

### Priority 5: Booking System
- [ ] Implement individual booking
- [ ] Implement group booking with guest names
- [ ] Add booking cancellation
- [ ] Create "My Bookings" page

### Priority 6: Social Features
- [ ] Connect Friends page to backend
- [ ] Implement friend requests
- [ ] Create friend profile viewing

### Priority 7: Additional Features
- [ ] Connect Event Suggestion to backend
- [ ] Implement profile editing
- [ ] Add proper error handling
- [ ] Implement loading states

---

## Critical Issues & Solutions

### Issue 1: Event Schema Mismatch
**Problem**: Frontend uses different field names than backend
**Solution**: 
- Change `image` → `imageUrl`
- Use `format` instead of separate indoor/outdoor
- Match `type` values exactly

### Issue 2: Region Values
**Problem**: EventCreation.vue has wrong region values
**Solution**: Use Singapore-specific regions (north, south, east, west, central)

### Issue 3: Missing State Management
**Problem**: No centralized state management
**Solution**: Install and configure Pinia for Vue 3

### Issue 4: FIN Field
**Problem**: Frontend has FIN field but backend doesn't store it
**Solution**: Add `finNumber` field to backend user schema

### Issue 5: Profile Completion
**Problem**: No mechanism to force profile completion
**Solution**: Create ProfileCompletion.vue and route guard

---

## State Management Structure (Pinia)

### Auth Store
```javascript
// stores/auth.js
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    profileCompleted: false,
    isAdmin: false,
    loading: false
  }),
  
  actions: {
    async login(phone, password) { /* ... */ },
    async logout() { /* ... */ },
    async checkProfileCompletion() { /* ... */ },
    async updateProfile(data) { /* ... */ }
  },
  
  getters: {
    canAccessAdmin: (state) => state.isAdmin,
    needsProfileCompletion: (state) => !state.profileCompleted
  }
})
```

### Events Store
```javascript
// stores/events.js
export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [],
    currentEvent: null,
    filters: {},
    loading: false
  }),
  
  actions: {
    async fetchEvents(filters) { /* ... */ },
    async fetchEventById(id) { /* ... */ },
    async bookEvent(eventId, type, guests) { /* ... */ }
  }
})
```

---

## Testing Checklist

### Authentication Flow
- [ ] User can sign up with phone + password + FIN
- [ ] User can login with phone + password
- [ ] Token is stored and used for API calls
- [ ] Logout clears all user data

### Profile Completion
- [ ] First-time users redirected to profile completion
- [ ] Cannot access other pages until complete
- [ ] All required fields validated
- [ ] Profile data saved correctly

### Event Management
- [ ] Events load from backend
- [ ] Filtering works correctly
- [ ] Event details display properly
- [ ] Images show placeholders when missing

### Booking System
- [ ] Individual booking works
- [ ] Group booking with guest names works
- [ ] Cannot double-book same event
- [ ] Can cancel bookings (24hr rule)

### Access Control
- [ ] Non-admin users cannot see "Create Event"
- [ ] Admin users can access admin features
- [ ] Sign in only shows when logged out

---

## Environment Variables

### Frontend (.env)
```
VUE_APP_API_URL=http://localhost:5000
VUE_APP_FIREBASE_API_KEY=your-api-key
VUE_APP_FIREBASE_AUTH_DOMAIN=your-auth-domain
VUE_APP_FIREBASE_PROJECT_ID=your-project-id
```

### Backend (.env)
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=../firebase/firebase-admin-key.json
FLASK_ENV=development
PORT=5000
```

---

## Quick Commands

### Frontend
```bash
cd NemoApp/frontend
npm install pinia         # State management
npm run serve             # Start dev server
npm run build            # Build for production
```

### Backend
```bash
cd NemoApp/backend
pip install -r requirements.txt
python app.py            # Start Flask server
```

### Testing
```bash
# Get Firebase token for testing
curl -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"6591234567@phone.local","password":"password123","returnSecureToken":true}'
```

---

## Notes

1. **Phone Authentication**: Uses email alias workaround to avoid SMS costs
2. **Admin Creation**: Admins must be created via Firebase Admin SDK with role='admin'
3. **Guest Bookings**: Group bookings support guest names without accounts
4. **Singapore Focus**: All regions, phone formats are Singapore-specific
5. **Profile Blocking**: Users cannot use the app until profile is complete

---

Last Updated: 2025-09-06