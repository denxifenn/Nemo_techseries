# Nemo Project - Status Checklist

Last updated: 2025-09-04 (UTC+8)

This document tracks backend progress against the agreed MVP scope. Links point to the implemented files and key functions.

## Summary

- Backend stack online (Flask + Firebase Admin).
- Auth flow working end-to-end (frontend signup via Firebase Auth, backend login + verify token).
- Events API implemented (list + details) on Firestore.
- Bookings implemented with atomic capacity checks:
  - Individual booking
  - Group booking supports existing user UIDs AND purely guest names via "groupMemberNames" (no login needed for those guests). Guest name seats stored as event.guestEntries.
- Profiles (view/update), Friends (send/accept/list), Admin Event Create, and Suggestions (free-text submit/list) implemented.
- Seed and verification scripts added for Firestore/Auth.

### Auth/UID Policy
- Normal users have Firebase-generated random, immutable UIDs; these are the canonical identifiers persisted across the backend and Firestore.
- Admin accounts may optionally be provisioned via the Firebase Admin SDK with custom, human-readable UIDs (e.g., "admin1"). Such provisioning is outside normal user signup; ensure users/{uid}.role = "admin".
- Signup/Login flow:
  - Frontend performs signup/login via Firebase Authentication (email + password) to obtain an ID token.
  - Backend never receives raw passwords; it verifies the ID token and extracts the UID on each request via [python.verify()](NemoApp/backend/api/auth.py:50) and decorators in [python.require_auth()](NemoApp/backend/utils/decorators.py:12).
  - On first successful login, the backend auto-creates users/{uid} in Firestore if missing.

## Kanban Alignment (MVP)

Completed
- [x] KAN-5 Research Firebase setup
- [x] KAN-6 Integrate Firebase with backend
- [x] KAN-7 Auth APIs (login/verify) → [backend/api/auth.py](NemoApp/backend/api/auth.py)
  - [python.login()](NemoApp/backend/api/auth.py:23)
  - [python.verify()](NemoApp/backend/api/auth.py:50)
- [x] KAN-8 Events list API → [backend/api/events.py](NemoApp/backend/api/events.py)
  - [python.list_events()](NemoApp/backend/api/events.py:12)
- [x] KAN-9 Event details API → [python.get_event()](NemoApp/backend/api/events.py:57)
- [x] KAN-10 Individual booking API → [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
- [x] KAN-11 Group booking API (now supports names) → [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)
- [x] KAN-12 Profile APIs (view/update) → [backend/api/profile.py](NemoApp/backend/api/profile.py)
  - [python.get_profile()](NemoApp/backend/api/profile.py:12), [python.update_profile()](NemoApp/backend/api/profile.py:29)
- [x] KAN-17/19 Friends APIs → [backend/api/friends.py](NemoApp/backend/api/friends.py)
  - [python.send_friend_request()](NemoApp/backend/api/friends.py:18)
  - [python.handle_friend_request()](NemoApp/backend/api/friends.py:63)
  - [python.list_friends()](NemoApp/backend/api/friends.py:105)
- [x] KAN-21 Admin create event → [python.create_event()](NemoApp/backend/api/admin.py:22)
- [x] KAN-23 Suggestions → [backend/api/suggestions.py](NemoApp/backend/api/suggestions.py)
  - [python.create_suggestion()](NemoApp/backend/api/suggestions.py:12)
  - [python.list_suggestions()](NemoApp/backend/api/suggestions.py:44)
- [x] Seed script (sample users/events/friendRequest) → [python.main()](NemoApp/backend/scripts/init_db.py:167)
- [x] Firebase verification script → [python.main()](NemoApp/backend/scripts/verify_firebase.py:6)
- [x] Auth decorators → [python.require_auth()](NemoApp/backend/utils/decorators.py:8), [python.require_admin()](NemoApp/backend/utils/decorators.py:27)
- [x] CORS-enabled app factory → [python.create_app()](NemoApp/backend/app.py:6)

In Progress
- [-] Test all APIs with Postman/CLI

Pending (in recommended order)
- [ ] Deployment to Render/Railway (MVP)
- [ ] Finalize Postman environment variables for team sharing (baseUrl, token, adminToken, web_api_key)
- [ ] Optional: add server-side validators module and refine error messages

## Implemented Endpoints (Backend)

Auth
- POST /api/auth/login → [python.login()](NemoApp/backend/api/auth.py:23)
- GET /api/auth/verify → [python.verify()](NemoApp/backend/api/auth.py:50)

Events
- GET /api/events → [python.list_events()](NemoApp/backend/api/events.py:12)
- GET /api/events/:id → [python.get_event()](NemoApp/backend/api/events.py:57)

Bookings
- POST /api/bookings/individual → [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
  - Body: {"eventId": "EVENT_ID"}
- POST /api/bookings/group → [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)
  - Body (supports both):
    - Existing user UIDs: "groupMembers": ["uid1","uid2"]
    - Pure guest names: "groupMemberNames": ["Alice","Bob"]
  - Behavior:
    - Includes initiator (current_user) automatically
    - Atomic capacity checks across UIDs + guest names
    - Prevents duplicate joins and duplicate guest-name entries per initiator
    - Event guest name seats persisted in "guestEntries"
- GET /api/bookings/my → [python.list_my_bookings()](NemoApp/backend/api/bookings.py:224)

Profiles
- GET /api/profile → [python.get_profile()](NemoApp/backend/api/profile.py:12)
- PUT /api/profile → [python.update_profile()](NemoApp/backend/api/profile.py:29)

Friends
- POST /api/friends/request → [python.send_friend_request()](NemoApp/backend/api/friends.py:18)
- PUT /api/friends/request/:id → [python.handle_friend_request()](NemoApp/backend/api/friends.py:63)
- GET /api/friends → [python.list_friends()](NemoApp/backend/api/friends.py:105)

Admin
- GET /api/admin/health → [python.admin_health()](NemoApp/backend/api/admin.py:12)
- POST /api/admin/events → [python.create_event()](NemoApp/backend/api/admin.py:22)

Suggestions
- POST /api/suggestions → [python.create_suggestion()](NemoApp/backend/api/suggestions.py:12)
- GET /api/suggestions → [python.list_suggestions()](NemoApp/backend/api/suggestions.py:44)

## Data Model Notes (MVP behavior)

- events:
  - participants: [uid, ...]
  - guestEntries: [{ name: string, addedBy: uid }, ...] for pure name bookings
  - currentParticipants tracks both participants + guestEntries

- bookings:
  - bookingType: "individual" | "group"
  - groupMembers: array of UIDs requested (deduped, includes initiator)
  - guestNames: array of guest strings (for group bookings with names)

## Test Checklist (CLI quick refs)

- Obtain idToken (Git Bash):
  - TOKEN=$(curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_WEB_API_KEY" -H "Content-Type: application/json" -d '{ "email": "you@example.com", "password": "Password123!", "returnSecureToken": true }' | jq -r '.idToken')

- Individual booking:
  - curl -X POST http://localhost:5000/api/bookings/individual -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "eventId": "EVENT_ID" }'

- Group booking with names only:
  - curl -X POST http://localhost:5000/api/bookings/group -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "eventId":"EVENT_ID", "groupMemberNames":["Alice","Bob"] }'

- Admin create event:
  - curl -X POST http://localhost:5000/api/admin/events -H "Authorization: Bearer ADMIN_TOKEN" -H "Content-Type: application/json" -d '{ "title":"New Event","description":"...","category":"sports","location":"Field A","date":"2025-12-31","time":"14:00","maxParticipants":20 }'

- Suggestions (free-text):
  - curl -X POST http://localhost:5000/api/suggestions -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "text":"Any feedback or suggestions for future events..." }'

## Changelog (Recent)

- Added Firestore-backed events list/detail → [backend/api/events.py](NemoApp/backend/api/events.py)
- Added individual/group bookings with transactions; group booking supports names → [backend/api/bookings.py](NemoApp/backend/api/bookings.py)
- Implemented Profiles (view/update) → [backend/api/profile.py](NemoApp/backend/api/profile.py)
- Implemented Friends (request/accept/list) → [backend/api/friends.py](NemoApp/backend/api/friends.py)
- Implemented Admin create event → [backend/api/admin.py](NemoApp/backend/api/admin.py)
- Simplified Suggestions to free-text and synced docs/tests → [backend/api/suggestions.py](NemoApp/backend/api/suggestions.py)
- Added Firebase verification + seed scripts → [backend/scripts](NemoApp/backend/scripts)
- Added Firestore Security Rules and Indexes → [firebase/firestore.rules](NemoApp/firebase/firestore.rules), [firebase/firestore.indexes.json](NemoApp/firebase/firestore.indexes.json)
- Added Postman collection for team testing → [tests/Nemo_backend.postman_collection.json](NemoApp/tests/Nemo_backend.postman_collection.json)
- Deployment readiness: WSGI entry + gunicorn + guide → [backend/wsgi.py](NemoApp/backend/wsgi.py), [backend/requirements.txt](NemoApp/backend/requirements.txt), [DEPLOYMENT_GUIDE.md](NemoApp/DEPLOYMENT_GUIDE.md)
- Firebase credentials path configurable via env → [backend/services/firebase_service.py](NemoApp/backend/services/firebase_service.py)
- Hardened auth with decorators → [backend/utils/decorators.py](NemoApp/backend/utils/decorators.py)
- Set CORS and blueprint registration → [backend/app.py](NemoApp/backend/app.py)
