# Nemo Backend — Firestore Collection Schemas (KAN-27..32)

This document defines the canonical schemas for the MVP Firestore collections, including:
- Field names, types, required/optional, constraints
- Example documents
- Invariants and how backend endpoints maintain them
- Suggested Firestore Security Rules and Indexes (to be applied next)

All schemas align with the implemented backend code. Endpoint implementations referenced below are in:
- [backend/api/auth.py](NemoApp/backend/api/auth.py)
  - [python.register()](NemoApp/backend/api/auth.py:6)
  - [python.login()](NemoApp/backend/api/auth.py:34)
  - [python.verify()](NemoApp/backend/api/auth.py:62)
- [backend/api/events.py](NemoApp/backend/api/events.py)
  - [python.list_events()](NemoApp/backend/api/events.py:12)
  - [python.get_event()](NemoApp/backend/api/events.py:57)
- [backend/api/bookings.py](NemoApp/backend/api/bookings.py)
  - [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
  - [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)
  - [python.list_my_bookings()](NemoApp/backend/api/bookings.py:224)
- [backend/api/profile.py](NemoApp/backend/api/profile.py)
  - [python.get_profile()](NemoApp/backend/api/profile.py:12)
  - [python.update_profile()](NemoApp/backend/api/profile.py:29)
- [backend/api/friends.py](NemoApp/backend/api/friends.py)
  - [python.send_friend_request()](NemoApp/backend/api/friends.py:18)
  - [python.handle_friend_request()](NemoApp/backend/api/friends.py:63)
  - [python.list_friends()](NemoApp/backend/api/friends.py:105)
- [backend/api/admin.py](NemoApp/backend/api/admin.py)
  - [python.create_event()](NemoApp/backend/api/admin.py:22)
- [backend/api/suggestions.py](NemoApp/backend/api/suggestions.py)
  - [python.create_suggestion()](NemoApp/backend/api/suggestions.py:12)
  - [python.list_suggestions()](NemoApp/backend/api/suggestions.py:44)

Backend uses Firebase Admin SDK via:
- [backend/services/firebase_service.py](NemoApp/backend/services/firebase_service.py)

Security decorators (Auth/Admin):
- [python.require_auth()](NemoApp/backend/utils/decorators.py:8)
- [python.require_admin()](NemoApp/backend/utils/decorators.py:27)

---

## 1) users (KAN-27)

Documents keyed by Firebase Auth UID.

Required fields:
- uid: string (Auth UID) — must equal document id
- email: string (lowercased)
- name: string (1..100)
- role: "user" | "admin" (default "user")
- friends: string[] of UIDs (default [])

Optional fields:
- profilePicture: string (URL)
- createdAt: timestamp
- updatedAt: timestamp

Example:
```json
{
  "uid": "u_123",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "user",
  "profilePicture": "",
  "friends": ["u_456", "u_789"],
  "createdAt": "2025-03-01T10:00:00Z"
}
```

Invariants:
- Document ID == uid.
- role is one of {"user","admin"}.
- friends array contains unique UIDs, no self-references.

Maintained by:
- Created on register: [python.register()](NemoApp/backend/api/auth.py:6)
- Updated on profile changes: [python.update_profile()](NemoApp/backend/api/profile.py:29)
- Mutated with ArrayUnion on friend accept: [python.handle_friend_request()](NemoApp/backend/api/friends.py:63)

Indexes:
- Query by email exact match (friends invite): single-field index on email (Firestore auto).

---

## 2) events (KAN-28)

Documents keyed by Firestore auto-ID.

Required fields:
- title: string
- description: string
- category: "sports" | "workshop" | "social"
- location: string
- date: string "YYYY-MM-DD"
- time: string "HH:MM" 24-hour
- maxParticipants: number > 0
- currentParticipants: number >= 0 (maintained by bookings)
- participants: string[] of UIDs (unique)
- createdBy: uid (admin)
- status: "upcoming" | "completed" | "cancelled"
- createdAt: timestamp

Optional fields:
- imageUrl: string
- guestEntries: array of { name: string, addedBy: uid } — added by group bookings with names

Example:
```json
{
  "title": "Football Match",
  "description": "Friendly game",
  "category": "sports",
  "imageUrl": "",
  "location": "Kallang",
  "date": "2025-12-31",
  "time": "14:00",
  "maxParticipants": 20,
  "currentParticipants": 7,
  "participants": ["u_123","u_456"],
  "guestEntries": [ { "name": "Alice", "addedBy": "u_123" } ],
  "createdBy": "admin_001",
  "status": "upcoming",
  "createdAt": "2025-03-01T10:00:00Z"
}
```

Invariants:
- 0 <= currentParticipants <= maxParticipants.
- currentParticipants == |participants| + |guestEntries|.
- participants must be unique UIDs.
- guestEntries unique per (addedBy, lower(name)) pair.

Maintained by:
- Creation: [python.create_event()](NemoApp/backend/api/admin.py:22)
- Read/list: [python.list_events()](NemoApp/backend/api/events.py:12), [python.get_event()](NemoApp/backend/api/events.py:57)
- Capacity updates (transactional): 
  - [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
  - [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)

Indexes:
- Composite index recommended:
  - where category == … order by date asc, time asc
  - where status == … order by date asc, time asc
  - Mixed category + status filters may require composite index per Firestore prompts.

---

## 3) bookings (KAN-29)

Documents keyed by Firestore auto-ID.

Required fields:
- eventId: string (ref id to events)
- userId: uid (booking creator / initiator)
- bookingType: "individual" | "group"
- status: "confirmed" (MVP)
- createdAt: timestamp

Optional fields:
- groupMembers: string[] UIDs (for group)
- guestNames: string[] names (for group with names)

Example (individual):
```json
{
  "eventId": "ev_001",
  "userId": "u_123",
  "bookingType": "individual",
  "groupMembers": [],
  "status": "confirmed",
  "createdAt": "2025-03-01T10:00:00Z"
}
```

Example (group with names):
```json
{
  "eventId": "ev_001",
  "userId": "u_123",
  "bookingType": "group",
  "groupMembers": ["u_123","u_456"], 
  "guestNames": ["Alice","Bob"],
  "status": "confirmed",
  "createdAt": "2025-03-01T11:00:00Z"
}
```

Invariants:
- For individual: creator must not already be in event participants.
- For group: seats consumed = new UIDs added + new guest names added.
- Double-book prevention for initiator enforced at transaction time.

Maintained by:
- [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
- [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)
- Read back for user: [python.list_my_bookings()](NemoApp/backend/api/bookings.py:224)

Indexes:
- where userId == current_user (single-field sufficient).

---

## 4) friendRequests (KAN-30)

Documents keyed by Firestore auto-ID.

Required fields:
- fromUserId: uid (sender)
- toUserId: uid (recipient)
- status: "pending" | "accepted" | "rejected"
- createdAt: timestamp

Example:
```json
{
  "fromUserId": "u_sender",
  "toUserId": "u_recipient",
  "status": "pending",
  "createdAt": "2025-03-01T12:00:00Z"
}
```

Invariants:
- There must not exist two opposing pending requests pair (A→B and B→A) at the same time.
- No duplicate pending requests in same direction.
- Only recipient can accept/reject.

Maintained by:
- Create: [python.send_friend_request()](NemoApp/backend/api/friends.py:18)
- Accept/Reject: [python.handle_friend_request()](NemoApp/backend/api/friends.py:63)

Indexes:
- where fromUserId == X and toUserId == Y and status == "pending"
- where toUserId == current_user and status == "pending" (for possible future UX)

---

## 5) suggestions (KAN-31)

Documents keyed by Firestore auto-ID.

Required fields:
- userId: uid (submitter)
- eventTitle: string
- eventDescription: string
- category: "sports" | "workshop" | "social"
- status: "pending" (MVP)
- createdAt: timestamp

Example:
```json
{
  "userId": "u_123",
  "eventTitle": "Cooking Class",
  "eventDescription": "Learn local dishes",
  "category": "workshop",
  "status": "pending",
  "createdAt": "2025-03-01T13:00:00Z"
}
```

Maintained by:
- Create: [python.create_suggestion()](NemoApp/backend/api/suggestions.py:12)
- Admin list: [python.list_suggestions()](NemoApp/backend/api/suggestions.py:44)

Indexes:
- orderBy createdAt desc for admin review queue (composite index might be prompted by Firestore).

---

## 6) admin (KAN-32)

Note: MVP implementation models admin via users.role == "admin". A separate "admins" collection is not necessary. If required by non-functional constraints, an optional `admins/{uid}` could be maintained redundantly.

Optional admin document:
```json
{
  "userId": "u_admin",
  "permissions": ["create_event"],
  "createdAt": "2025-03-01T09:00:00Z"
}
```

Source of truth:
- Role check in users: [python.require_admin()](NemoApp/backend/utils/decorators.py:27)

---

## Security Rules (Preview)

These pair with the schemas above. We will place the full rules in `NemoApp/firebase/firestore.rules` next.

Principles:
- Users can read public events.
- Users can read/write their own user profile limited fields (name, profilePicture).
- Users can create bookings but cannot modify event counters directly (server maintains).
- Friend requests: sender creates; only recipient can accept/reject.
- Suggestions: any authenticated user can create; only admins can list all.

High-level snippets (for reference; full file to follow):
```js
// pseudo-rules, final file will be added as firebase/firestore.rules

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isSignedIn() { return request.auth != null; }
    function isSelf(uid) { return isSignedIn() && request.auth.uid == uid; }
    function isAdmin() {
      return isSignedIn() && get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == "admin";
    }

    match /users/{uid} {
      allow read: if isSelf(uid) || isAdmin();
      allow update: if isSelf(uid) && request.resource.data.diff(resource.data).changedKeys().hasOnly(["name","profilePicture","updatedAt"]);
      allow create: if false; // created via Admin SDK on backend
    }

    match /events/{eventId} {
      allow read: if true;
      allow create, update, delete: if isAdmin();
    }

    match /bookings/{bookingId} {
      allow read: if isSignedIn();
      allow create: if isSignedIn();
      allow update, delete: if false; // booking state controlled by server
    }

    match /friendRequests/{id} {
      allow create: if isSignedIn();
      allow read: if isSignedIn() && (resource.data.fromUserId == request.auth.uid || resource.data.toUserId == request.auth.uid) || isAdmin();
      allow update: if isSignedIn() && resource.data.toUserId == request.auth.uid; // accept/reject by recipient
    }

    match /suggestions/{id} {
      allow create: if isSignedIn();
      allow read: if isAdmin(); // list for admins only
    }
  }
}
```

We will add the concrete rules file next so it can be deployed via `firebase deploy --only firestore:rules`.

---

## Suggested Composite Indexes

We will add a helper file `NemoApp/firebase/firestore.indexes.json` next. Expect Firestore to prompt for indexes after you run queries; specifically:

- events
  - where: category == …; orderBy: date asc, time asc
  - where: status == …; orderBy: date asc, time asc
  - Optionally both category/status together if used simultaneously

---

## Validation Helpers (Optional)

A thin validation layer can be added to centralize input checks before writing to Firestore.

Proposed location:
- `backend/utils/validators.py`
  - validate_name(str)
  - validate_category(str)
  - validate_date("YYYY-MM-DD")
  - validate_time("HH:MM")
  - validate_max_participants(int)

Current endpoints include minimal inline validation:
- [python.create_event()](NemoApp/backend/api/admin.py:22)
- [python.update_profile()](NemoApp/backend/api/profile.py:29)

---

## Migration Notes

- Existing data created by the seed script already matches these schemas:
  - [python.main()](NemoApp/backend/scripts/init_db.py:167)
- If you previously stored events without `guestEntries`, those fields will be added lazily by group bookings.
- Ensure all event docs contain `currentParticipants`, `participants`, `maxParticipants`.

---

## Next Steps

1) Add and deploy Firestore Security Rules (file: `NemoApp/firebase/firestore.rules`).
2) Add and deploy composite indexes (file: `NemoApp/firebase/firestore.indexes.json`).
3) Optionally add `backend/utils/validators.py` and refactor endpoints to use it.

This completes KAN-27..31 schema definitions (KAN-32 is satisfied via role in users).