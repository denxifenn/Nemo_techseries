# Nemo Project - Status Checklist

Last updated: 2025-09-03 (UTC+8)

This document tracks backend progress against the agreed MVP scope. Links point to the implemented files and key functions.

## Summary

- Backend stack online (Flask + Firebase Admin).
- Core read endpoints for Events implemented with Firestore.
- Bookings implemented with atomic capacity checks (individual + group).
- Auth flow working end-to-end (register, verify token, login).
- Seed and verification scripts added for Firestore/Auth.

## Kanban Alignment (MVP)

Completed
- [x] KAN-5 Research Firebase setup
- [x] KAN-6 Integrate Firebase with backend
- [x] KAN-7 Auth APIs (register/login/verify) → [backend/api/auth.py](NemoApp/backend/api/auth.py)
  - [python.register()](NemoApp/backend/api/auth.py:6)
  - [python.login()](NemoApp/backend/api/auth.py:34)
  - [python.verify()](NemoApp/backend/api/auth.py:62)
- [x] KAN-8 Events list API → [backend/api/events.py](NemoApp/backend/api/events.py)
  - [python.list_events()](NemoApp/backend/api/events.py:12)
- [x] KAN-9 Event details API → [python.get_event()](NemoApp/backend/api/events.py:57)
- [x] KAN-10 Individual booking API → [python.create_individual_booking()](NemoApp/backend/api/bookings.py:18)
- [x] KAN-11 Group booking API → [python.create_group_booking()](NemoApp/backend/api/bookings.py:70)
- [x] Seed script (sample users/events/friendRequest) → [python.main()](NemoApp/backend/scripts/init_db.py:167)
- [x] Firebase verification script → [python.main()](NemoApp/backend/scripts/verify_firebase.py:6)
- [x] Auth decorators → [python.require_auth()](NemoApp/backend/utils/decorators.py:8), [python.require_admin()](NemoApp/backend/utils/decorators.py:27)
- [x] CORS-enabled app factory → [python.create_app()](NemoApp/backend/app.py:6)

In Progress
- [-] Test all APIs with Postman/CLI

Pending (in recommended order)
- [ ] KAN-12 Profile APIs (view/update) → [backend/api/profile.py](NemoApp/backend/api/profile.py)
  - Wire Firestore for [python.get_profile()](NemoApp/backend/api/profile.py:12), [python.update_profile()](NemoApp/backend/api/profile.py:26)
- [ ] KAN-17/19 Friends APIs → [backend/api/friends.py](NemoApp/backend/api/friends.py)
  - [python.send_friend_request()](NemoApp/backend/api/friends.py:14)
  - [python.handle_friend_request()](NemoApp/backend/api/friends.py:29)
  - [python.list_friends()](NemoApp/backend/api/friends.py:43)
- [ ] KAN-21 Admin create event → [python.create_event()](NemoApp/backend/api/admin.py:28)
- [ ] KAN-23 Suggestions → [backend/api/suggestions.py](NemoApp/backend/api/suggestions.py)
  - [python.create_suggestion()](NemoApp/backend/api/suggestions.py:12)
  - [python.list_suggestions()](NemoApp/backend/api/suggestions.py:24)
- [ ] Collection schema codification (docs/validators):
  - KAN-27 users
  - KAN-28 events
  - KAN-29 bookings
  - KAN-30 friend_requests
  - KAN-31 suggestions
  - KAN-32 admin

## Implemented Endpoints (Backend)

Auth
- POST /api/auth/register → [python.register()](NemoApp/backend/api/auth.py:6)
- POST /api/auth/login → [python.login()](NemoApp/backend/api/auth.py:34)
- GET /api/auth/verify → [python.verify()](NemoApp/backend/api/auth.py:62)

Events
- GET /api/events → [python.list_events()](NemoApp/backend/api/events.py:12)
- GET /api/events/:id → [python.get_event()](NemoApp/backend/api/events.py:57)

Bookings
- POST /api/bookings/individual → [python.create_individual_booking()](NemoApp/backend/api/bookings.py:18)
- POST /api/bookings/group → [python.create_group_booking()](NemoApp/backend/api/bookings.py:70)
- GET /api/bookings/my → [python.list_my_bookings()](NemoApp/backend/api/bookings.py:130)

Utilities
- Firebase Admin service → [python.FirebaseService](NemoApp/backend/services/firebase_service.py:1)
- Decorators → [python.require_auth()](NemoApp/backend/utils/decorators.py:8), [python.require_admin()](NemoApp/backend/utils/decorators.py:27)
- Firestore seed → [python.main()](NemoApp/backend/scripts/init_db.py:167)
- Firebase verify → [python.main()](NemoApp/backend/scripts/verify_firebase.py:6)

## What’s left to implement

1) Profiles (KAN-12)
- GET /api/profile, PUT /api/profile
- Firestore: users/{uid} (fields: name, profilePicture, etc.)
- Add minimal server-side validation before write

2) Friends (KAN-17, KAN-19)
- POST /api/friends/request (by email)
- PUT /api/friends/request/:id (accept/reject)
- GET /api/friends (resolve friend IDs to profiles)
- Firestore: friendRequests, users.friends[]

3) Admin + Suggestions
- POST /api/admin/events (role: admin)
- Suggestions POST/GET (admin) with Firestore collections

4) Collection Schema Notes (MVP)
- users: uid, email, name, role, profilePicture, friends[], createdAt
- events: title, description, category, imageUrl, location, date(YYYY-MM-DD), time(HH:MM), maxParticipants, currentParticipants, participants[], createdBy, status, createdAt
- bookings: eventId, userId, bookingType, groupMembers[], status, createdAt
- friendRequests: fromUserId, toUserId, status, createdAt
- suggestions: userId, eventTitle, eventDescription, category, status, createdAt

## Testing Coverage (Executed)

- Firebase Admin connectivity → PASS using [python.main()](NemoApp/backend/scripts/verify_firebase.py:6)
- Seed data writes/reads → PASS using [python.main()](NemoApp/backend/scripts/init_db.py:167)
- Auth flow → PASS (register → signIn via REST → idToken → verify/login)
- Events list/details → PASS (reads from Firestore)
- Bookings (individual/group) → PASS with transactional capacity checks and duplicate prevention

## Next Steps (Suggested)

1) Implement Profiles (KAN-12) in [backend/api/profile.py](NemoApp/backend/api/profile.py)
2) Implement Friends (KAN-17, KAN-19) in [backend/api/friends.py](NemoApp/backend/api/friends.py)
3) Implement Admin create event (KAN-21) in [backend/api/admin.py](NemoApp/backend/api/admin.py)
4) Implement Suggestions (KAN-23) in [backend/api/suggestions.py](NemoApp/backend/api/suggestions.py)
5) Prepare Postman collection and export to repo under /NemoApp/tests/postman_collection.json
6) Decide deployment target (Render/Railway) and add Procfile or service file

## Changelog (Recent)

- Added Firestore-backed events list/detail → [backend/api/events.py](NemoApp/backend/api/events.py)
- Added individual/group bookings with transactions → [backend/api/bookings.py](NemoApp/backend/api/bookings.py)
- Added Firebase verification + seed scripts → [backend/scripts](NemoApp/backend/scripts)
- Hardened auth with decorators → [backend/utils/decorators.py](NemoApp/backend/utils/decorators.py)
- Set CORS and blueprint registration → [backend/app.py](NemoApp/backend/app.py)
