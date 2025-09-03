# Nemo Backend Testing Guide (aligned with PROJECT_STATUS.md)

This guide explains exactly how to verify all completed MVP backend features using Windows Git Bash or Postman. It pairs with the project status tracker at [PROJECT_STATUS.md](NemoApp/PROJECT_STATUS.md).

Prerequisites
- Windows Git Bash terminal
- Python 3.8+ (venv created as .venv)
- Backend running locally
  - source .venv/Scripts/activate
  - python NemoApp/backend/app.py
- Firebase setup is verified (service account at NemoApp/firebase/firebase-admin-key.json)
  - Optional verifier: [python.main()](NemoApp/backend/scripts/verify_firebase.py:6)
- Optional seed data (sample users/events):
  - python NemoApp/backend/scripts/init_db.py

Useful References (code)
- App entry: [backend/app.py](NemoApp/backend/app.py)
- Events API: [python.list_events()](NemoApp/backend/api/events.py:12), [python.get_event()](NemoApp/backend/api/events.py:57)
- Bookings API: 
  - [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
  - [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)
  - [python.list_my_bookings()](NemoApp/backend/api/bookings.py:224)
- Profile API: [python.get_profile()](NemoApp/backend/api/profile.py:12), [python.update_profile()](NemoApp/backend/api/profile.py:29)
- Friends API: [python.send_friend_request()](NemoApp/backend/api/friends.py:18), [python.handle_friend_request()](NemoApp/backend/api/friends.py:63), [python.list_friends()](NemoApp/backend/api/friends.py:105)
- Admin API: [python.create_event()](NemoApp/backend/api/admin.py:22)
- Suggestions API: [python.create_suggestion()](NemoApp/backend/api/suggestions.py:12), [python.list_suggestions()](NemoApp/backend/api/suggestions.py:44)

Conventions used below
- We assume the backend base URL is http://localhost:5000.
- Use single quotes around JSON bodies in Git Bash.
- Optional jq extraction is shown; if not installed, just read the raw JSON.

01) Obtain a Firebase idToken (normal user)
1. Register user (only once):
   curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d '{ "email":"you@example.com", "password":"Password123!", "name":"Your Name" }'
2. Get Web API Key:
   - Firebase Console → Project settings → General → “Web API Key”
3. Sign in via Firebase REST to get idToken (replace YOUR_WEB_API_KEY):
   TOKEN=$(curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_WEB_API_KEY" -H "Content-Type: application/json" -d '{ "email":"you@example.com", "password":"Password123!", "returnSecureToken": true }' | jq -r '.idToken')
4. Optional: verify token with backend:
   curl -s -X GET http://localhost:5000/api/auth/verify -H "Authorization: Bearer $TOKEN" | jq

02) Events (KAN-8, KAN-9)
- List events:
  curl -s http://localhost:5000/api/events | jq
- View one event:
  curl -s http://localhost:5000/api/events/EVENT_ID | jq
Success criteria:
- 200 OK with events array for list
- 200 OK with event object for details

03) Bookings – Individual (KAN-10)
- Book:
  curl -s -X POST http://localhost:5000/api/bookings/individual -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "eventId": "EVENT_ID" }' | jq
- Duplicate booking guard:
  - repeat the same command → 400 with "User already joined this event"
- Capacity guard:
  - if event is full → 400 with "Event is full"
- Validate event counters:
  curl -s http://localhost:5000/api/events/EVENT_ID | jq
  - currentParticipants increases
  - participants contains your uid
Success criteria:
- 201 Created for first booking
- Event counters consistent with one seat consumed

04) Bookings – Group with Names (KAN-11)
- Book with guest names only (no accounts for guests):
  curl -s -X POST http://localhost:5000/api/bookings/group -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "eventId":"EVENT_ID", "groupMemberNames":["Alice","Bob"] }' | jq
- Mixed mode (UIDs + guest names) also works:
  curl -s -X POST http://localhost:5000/api/bookings/group -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "eventId":"EVENT_ID", "groupMembers":["some_friend_uid"], "groupMemberNames":["Charlie"] }' | jq
- Validate:
  - Event guestEntries updated with objects like {name:"Alice", addedBy:"<your-uid>"}
  - currentParticipants increased by number of new seats
Check event doc:
  curl -s http://localhost:5000/api/events/EVENT_ID | jq
Success criteria:
- 201 Created with joinedCount showing number of newly-added seats
- guestEntries recorded for names; participants updated for UIDs

05) My Bookings
- Show all your bookings with event snippets:
  curl -s -X GET http://localhost:5000/api/bookings/my -H "Authorization: Bearer $TOKEN" | jq
Success criteria:
- 200 OK with array, each booking includes event summary fields

06) Profile (KAN-12)
- View profile:
  curl -s -X GET http://localhost:5000/api/profile -H "Authorization: Bearer $TOKEN" | jq
- Update name or profile picture:
  curl -s -X PUT http://localhost:5000/api/profile -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "name":"New Name" }' | jq
Success criteria:
- 200 OK with the updated fields echoed back
- Subsequent GET includes updated data

07) Friends (KAN-17, KAN-19)
- As you (sender), send request by email:
  curl -s -X POST http://localhost:5000/api/friends/request -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "email":"friend@example.com" }' | jq
- As the recipient, accept request:
  curl -s -X PUT http://localhost:5000/api/friends/request/REQUEST_ID -H "Authorization: Bearer $FRIEND_TOKEN" -H "Content-Type: application/json" -d '{ "action":"accept" }' | jq
- List my friends:
  curl -s -X GET http://localhost:5000/api/friends -H "Authorization: Bearer $TOKEN" | jq
Success criteria:
- Prevents: sending to self, duplicate pending requests, adding existing friends
- On accept: both users have each other in friends arrays

08) Admin – Create Event (KAN-21)
- Promote a user to admin in Firestore (users/{uid}.role = "admin"), then refresh token.
- Create a new event (admin only):
  curl -s -X POST http://localhost:5000/api/admin/events -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{ "title":"Community Football","description":"Friendly match","category":"sports","location":"Kallang","date":"2025-12-31","time":"14:00","maxParticipants":20 }' | jq
Success criteria:
- 201 Created with eventId
- New event appears in GET /api/events

09) Suggestions (KAN-23)
- Submit suggestion (normal user):
  curl -s -X POST http://localhost:5000/api/suggestions -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{ "title":"Cooking Class","description":"Learn local dishes","category":"workshop" }' | jq
- List suggestions (admin only):
  curl -s -X GET http://localhost:5000/api/suggestions -H "Authorization: Bearer $ADMIN_TOKEN" | jq
Success criteria:
- POST returns 201 with suggestionId
- Admin list shows suggestions with user info if available

10) Postman Setup (optional but recommended)
- Create environment:
  - baseUrl = http://localhost:5000
  - token = YOUR_ID_TOKEN
  - adminToken = YOUR_ADMIN_ID_TOKEN
- Import requests mirroring the curl calls above.
- For protected requests, set Authorization to “Bearer {{token}}”.

11) Expected error messages (sanity)
- 401 Unauthorized → missing/invalid Authorization header
- 403 Admin access required → non-admin on admin routes
- 400 Bad Request
  - register: missing fields
  - bookings: event full, already joined, only old participants
  - admin create: missing fields, invalid category/date/time
- 404 Not Found → invalid event or friend request id

12) Quick mapping to PROJECT_STATUS.md
- Bookings (individual + group names): Completed
- Profiles (view/update): Completed
- Friends (request/accept/list): Completed
- Admin create event: Completed
- Suggestions (submit/list): Completed
- Testing status: In Progress (keep this guide handy while testing)

Troubleshooting
- Token expired:
  - Re-run the REST sign-in command to get a fresh idToken.
- “User not found” for friends:
  - Recipient must have registered via backend so a users/{uid} doc exists.
- Capacity errors:
  - Confirm event.maxParticipants and currentParticipants in the event doc.
