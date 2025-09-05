# Nemo Backend — Firestore Collection Schemas (KAN-27..32)

This document defines the canonical schemas for the MVP Firestore collections, including:
- Field names, types, required/optional, constraints
- Example documents
- Invariants and how backend endpoints maintain them
- Suggested Firestore Security Rules and Indexes (to be applied next)

All schemas align with the implemented backend code. Endpoint implementations referenced below are in:
- [backend/api/auth.py](NemoApp/backend/api/auth.py)
  - [python.login()](NemoApp/backend/api/auth.py:23)
  - [python.verify()](NemoApp/backend/api/auth.py:50)
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
 
UID Policy and Signup/Login Flow
- Normal users receive Firebase-generated random, immutable UIDs on registration/sign-in. These are used as document IDs in users/{uid} and throughout Firestore/backend.
- Admin accounts may be provisioned externally via the Firebase Admin SDK with a custom, human-readable UID (e.g., "admin1"). This provisioning is outside normal user signup; ensure users/{uid}.role = "admin".
- Signup/login (finalized):
  - Frontend performs signup and login using Firebase Auth (email/password) to obtain an ID token. The backend never receives raw passwords.
  - Backend verifies ID tokens on requests. On the first successful login, the backend auto-creates users/{uid} if it does not exist. See [python.login()](NemoApp/backend/api/auth.py:23) and [python.verify()](NemoApp/backend/api/auth.py:50).
 
## 1) users (KAN-27)
 
Documents keyed by Firebase Auth UID.
 
Required fields:
- uid: string (Auth UID) — must equal document id
- phoneNumber: string (E.164, e.g. +6591234567)
- fullName: string (1..100)
- age: number (integer 18..100)
- nationality: string (2..50)
- languages: string[] (1..10, each 2..30 chars)
- homeCountry: string (2..50)
- restDays: string[] (non-empty; values in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
- role: "user" | "admin" (default "user")
- friends: string[] of UIDs (default [])
 
Optional fields:
- interests: string[] (0..20, each 1..50 chars)
- skills: { name: string(1..50), rating: "Basic"|"Proficient"|"Expert" }[] (0..20)
- profilePicture: string (URL)
- profileCompleted: boolean (derived; true when all required fields present/valid)
- profileCompletedAt: timestamp (first time profileCompleted became true)
- createdAt: timestamp
- updatedAt: timestamp
- name: string (legacy mirror of fullName for backwards compatibility)
 
Example:
```json
{
  "uid": "u_123",
  "phoneNumber": "+6591234567",
  "fullName": "John Doe",
  "age": 28,
  "nationality": "Singaporean",
  "languages": ["English", "Mandarin"],
  "homeCountry": "Singapore",
  "restDays": ["Saturday", "Sunday"],
  "interests": ["Football", "Cooking"],
  "skills": [
    {"name": "Cooking", "rating": "Proficient"},
    {"name": "Programming", "rating": "Expert"}
  ],
  "role": "user",
  "profilePicture": "",
  "friends": ["u_456", "u_789"],
  "profileCompleted": true,
  "profileCompletedAt": "2025-03-01T10:00:00Z",
  "createdAt": "2025-03-01T10:00:00Z",
  "updatedAt": "2025-03-01T11:00:00Z"
}
```
 
Invariants:
- Document ID == uid.
- role is one of {"user","admin"}.
- friends array contains unique UIDs, no self-references.
- skills.rating must be one of {"Basic","Proficient","Expert"}.
- restDays values must be valid weekdays.
 
Maintained by:
- Created automatically on first backend login (auto-provision) via ensure_user_doc in [backend/services/firebase_service.py](NemoApp/backend/services/firebase_service.py) called from [backend/api/auth.py](NemoApp/backend/api/auth.py)
- Updated on profile changes: [backend/api/profile.py](NemoApp/backend/api/profile.py)
- Mutated with ArrayUnion on friend accept: [backend/api/friends.py](NemoApp/backend/api/friends.py)
 
Indexes:
- Query by phoneNumber exact match (for invites or lookup): single-field index on phoneNumber (Firestore auto).
 
---

## 2) events (KAN-28)

Documents keyed by Firestore auto-ID.

Required fields:
- title: string
- description: string
- format: "online" | "offline"
- venueType: "indoor" | "outdoor" (required iff format == "offline")
- type: "sports" | "arts" | "culture" | "music" | "performance" | "workshop" | "tours" | "other"
- region: "north" | "south" | "east" | "west" | "central"
- organiser: string (free-text)
- location: string
- date: string "YYYY-MM-DD" (single-day event)
- startTime: string "HH:MM" 24-hour (SGT)
- endTime: string "HH:MM" 24-hour (SGT)
- timing: "morning" | "afternoon" | "evening" | "night" (derived from start/end in SGT)
- price: number (SGD; allow 0 for free)
- maxParticipants: number > 0
- currentParticipants: number >= 0 (maintained by bookings)
- participants: string[] of UIDs (unique)
- createdBy: uid (admin)
- status: "upcoming" | "completed" | "cancelled"
- createdAt: timestamp

Optional fields:
- imageUrl: string
- guestEntries: array of { name: string, addedBy: uid } — added by group bookings with names

Computed in responses (not stored):
- availableSlots: number = maxParticipants - currentParticipants

Example:
```json
{
  "title": "Community Drum Circle",
  "description": "Learn basic rhythms together.",
  "format": "offline",
  "venueType": "outdoor",
  "type": "music",
  "region": "central",
  "organiser": "Community Arts Group",
  "location": "Esplanade Outdoor Theatre",
  "date": "2025-12-31",
  "startTime": "18:30",
  "endTime": "20:00",
  "timing": "evening",
  "price": 0,
  "imageUrl": "",
  "maxParticipants": 50,
  "currentParticipants": 7,
  "participants": ["u_123","u_456"],
  "guestEntries": [ { "name": "Alice", "addedBy": "u_123" } ],
  "createdBy": "admin_001",
  "status": "upcoming",
  "createdAt": "2025-03-01T10:00:00Z"
}
```

Invariants:
- Single-day event: only one `date`
- Time order: startTime < endTime (within the same date, SGT)
- Timing bucket derivation (SGT):
  - morning: 06:00–11:59
  - afternoon: 12:00–17:59
  - evening: 18:00–21:59
  - night: 22:00–05:59
  If an event spans multiple buckets, use the bucket of startTime.
- format == "online" implies venueType is absent
- format == "offline" implies venueType in {"indoor","outdoor"}
- price >= 0
- 0 <= currentParticipants <= maxParticipants
- currentParticipants == |participants| + |guestEntries|
- participants must be unique UIDs
- guestEntries unique per (addedBy, lower(name)) pair

Maintained by:
- Creation: [python.create_event()](NemoApp/backend/api/admin.py:34)
- Read/list:
  - [python.list_events()](NemoApp/backend/api/events.py:12)
  - [python.get_event()](NemoApp/backend/api/events.py:64)
- Capacity updates (transactional):
  - [python.create_individual_booking()](NemoApp/backend/api/bookings.py:16)
  - [python.create_group_booking()](NemoApp/backend/api/bookings.py:83)

Filters (API support to be added/extended):
- format, type, region
- date range: fromDate..toDate (inclusive)
- timing: morning|afternoon|evening|night (derived)
- price range: minPrice..maxPrice (optional)
- category/status kept for backwards compatibility (legacy)

Indexes (recommended composites; Firestore may prompt exact specs):
- where format == … orderBy date asc, startTime asc
- where type == … orderBy date asc, startTime asc
- where region == … orderBy date asc, startTime asc
- optional: where status == … orderBy date asc, startTime asc
- optional: compound filters (format+type, type+region) as usage dictates

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
- text: string (1..2000)
- createdAt: timestamp

Example:
```json
{
  "userId": "u_123",
  "text": "Please organise more football friendlies on Sundays evening.",
  "createdAt": "2025-03-01T13:00:00Z"
}
```

Maintained by:
- Create (free-text only): [python.create_suggestion()](NemoApp/backend/api/suggestions.py:10)
- Admin list: [python.list_suggestions()](NemoApp/backend/api/suggestions.py:42)

Indexes:
- orderBy createdAt desc for admin review queue.

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
      allow update: if isSelf(uid) && request.resource.data.diff(resource.data).changedKeys().hasOnly(["name","fullName","age","nationality","languages","homeCountry","restDays","interests","skills","profilePicture","updatedAt"]);
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