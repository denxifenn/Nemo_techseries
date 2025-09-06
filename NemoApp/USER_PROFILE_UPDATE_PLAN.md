# User Profile Update Implementation Plan

## Overview
This plan details the implementation of enhanced user profiles with mandatory fields that users must complete after initial signup. The backend will enforce profile completion before users can access main app features. Authentication continues to use phone numbers (stored as email aliases in Firebase Auth).

## New User Profile Schema

### Current Fields (Keeping)
- `uid`: string (Firebase Auth UID)
- `phoneNumber`: string (+65XXXXXXXX format) - primary identifier
- `name`: string (will be renamed to fullName)
- `role`: "user" | "admin"
- `profilePicture`: string (URL)
- `friends`: string[] (UIDs)
- `createdAt`: timestamp
- `updatedAt`: timestamp

### New Required Fields
- `fullName`: string (replacing 'name', required, 1-100 chars)
- `age`: number (required, 18-100)
- `nationality`: string (required, e.g., "Singaporean", "Malaysian", etc.)
- `languages`: string[] (required, at least 1, e.g., ["English", "Mandarin"])
- `homeCountry`: string (required, e.g., "Singapore", "Malaysia")
- `restDays`: string[] (required, weekdays e.g., ["Saturday", "Sunday"])

### New Optional Fields (User can add/edit)
- `interests`: string[] (optional initially, can be empty array)
- `skills`: array of objects (optional initially, can be empty array)
  ```json
  {
    "name": "Cooking",
    "rating": "Expert" // "Basic" | "Proficient" | "Expert"
  }
  ```

### System Fields (Auto-managed)
- `profileCompleted`: boolean (auto-calculated, true when all required fields are filled)
- `profileCompletedAt`: timestamp (when profile was first completed)

## Implementation Steps

### 1. Backend Profile API Updates (`/api/profile`)

#### GET `/api/profile`
- Returns complete user profile including new fields
- Includes `profileCompleted` status

#### PUT `/api/profile` 
- Accepts all new fields for update
- Validates required fields:
  - fullName: 1-100 characters
  - age: 18-100
  - nationality: non-empty string
  - languages: array with at least 1 language
  - homeCountry: non-empty string
  - restDays: array of valid weekdays
- Validates optional fields:
  - interests: array of strings
  - skills: array of {name: string, rating: "Basic"|"Proficient"|"Expert"}
- Automatically sets `profileCompleted` = true when all required fields are present
- Sets `profileCompletedAt` timestamp on first completion

#### GET `/api/profile/completion-status`
- Returns whether profile is complete
- Lists missing required fields if incomplete
```json
{
  "profileCompleted": false,
  "missingFields": ["age", "nationality", "languages"],
  "completedFields": ["fullName", "phoneNumber", "homeCountry", "restDays"]
}
```

### 2. Validation Rules

#### Required Field Validations
- `fullName`: 
  - Type: string
  - Length: 1-100 characters
  - Pattern: At least one non-whitespace character
  
- `age`:
  - Type: number
  - Range: 18-100
  - Must be integer
  
- `nationality`:
  - Type: string
  - Length: 2-50 characters
  - Common values: "Singaporean", "Malaysian", "Indonesian", "Filipino", "Indian", "Chinese", etc.
  
- `languages`:
  - Type: array of strings
  - Minimum: 1 language
  - Maximum: 10 languages
  - Each language: 2-30 characters
  - Common values: "English", "Mandarin", "Malay", "Tamil", "Hindi", "Bengali", etc.
  
- `homeCountry`:
  - Type: string
  - Length: 2-50 characters
  - Common values: "Singapore", "Malaysia", "Indonesia", "Philippines", "India", "China", etc.
  
- `restDays`:
  - Type: array of strings
  - Values must be from: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  - Can be empty array (no rest days) or up to 7 days

#### Optional Field Validations
- `interests`:
  - Type: array of strings
  - Maximum: 20 interests
  - Each interest: 1-50 characters
  
- `skills`:
  - Type: array of objects
  - Maximum: 20 skills
  - Each skill object:
    - name: string, 1-50 characters
    - rating: must be "Basic", "Proficient", or "Expert"

### 3. Firebase Service Updates

Update `FirebaseService.ensure_user_doc()` in [`firebase_service.py`](NemoApp/backend/services/firebase_service.py) to include new fields with defaults:
- Rename existing 'name' field to 'fullName'
- Set empty arrays for array fields (interests, skills, languages, restDays)
- Set null for unspecified fields (age, nationality, homeCountry)
- Calculate `profileCompleted` based on presence of required fields

### 4. Database Migration

For existing users:
- Migrate 'name' field to 'fullName'
- Add new fields with null/empty values
- Set `profileCompleted` = false
- Frontend will prompt for completion on next login

### 5. API Response Formats

#### Complete Profile Response
```json
{
  "success": true,
  "profile": {
    "uid": "user_123",
    "phoneNumber": "+6591234567",
    "fullName": "John Doe",
    "age": 28,
    "nationality": "Singaporean",
    "languages": ["English", "Mandarin"],
    "homeCountry": "Singapore",
    "restDays": ["Saturday", "Sunday"],
    "interests": ["Football", "Cooking", "Reading"],
    "skills": [
      {"name": "Programming", "rating": "Expert"},
      {"name": "Cooking", "rating": "Proficient"}
    ],
    "role": "user",
    "profilePicture": "",
    "friends": [],
    "profileCompleted": true,
    "profileCompletedAt": "2025-03-01T10:00:00Z",
    "createdAt": "2025-02-28T10:00:00Z",
    "updatedAt": "2025-03-01T10:00:00Z"
  }
}
```

#### Profile Completion Status Response
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

#### Profile Update Request Body
```json
{
  "fullName": "John Doe",
  "age": 28,
  "nationality": "Singaporean",
  "languages": ["English", "Mandarin", "Malay"],
  "homeCountry": "Singapore",
  "restDays": ["Saturday", "Sunday"],
  "interests": ["Football", "Cooking"],
  "skills": [
    {"name": "Web Development", "rating": "Expert"},
    {"name": "Photography", "rating": "Basic"}
  ]
}
```

### 6. Updated Files Structure

Files that need modification:
1. [`backend/api/profile.py`](NemoApp/backend/api/profile.py) - Add new endpoints and field handling
2. [`backend/services/firebase_service.py`](NemoApp/backend/services/firebase_service.py) - Update ensure_user_doc()
3. [`backend/scripts/init_db.py`](NemoApp/backend/scripts/init_db.py) - Update seed data with new fields
4. [`backend/utils/validators.py`](NemoApp/backend/utils/validators.py) - NEW FILE for field validations
5. [`DATA_SCHEMAS.md`](NemoApp/DATA_SCHEMAS.md) - Update documentation with new schema

### 7. Frontend Flow (Future Implementation)

1. User signs up with phone and password
2. Backend creates basic profile with phoneNumber
3. On first login after signup:
   - Call `/api/profile/completion-status`
   - If incomplete, redirect to profile completion screen
   - Show form with all required fields
   - Validate and submit to PUT `/api/profile`
4. Allow profile editing anytime via Profile page
5. For existing users, prompt for completion on next login

### 8. Testing Strategy

Create test cases for:
- Profile creation with all fields
- Profile update with partial fields
- Validation of each required field
- Skill rating validation
- Rest days validation (weekday values)
- Profile completion status calculation
- Backward compatibility with existing users
- Migration of 'name' to 'fullName'

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/profile` | Get current user's complete profile |
| PUT | `/api/profile` | Update user profile fields |
| GET | `/api/profile/completion-status` | Check if profile is complete |

## Implementation Priority

1. **Phase 1 - Backend (Current Focus)**
   - Update Firebase service to handle new fields
   - Implement profile API with validation
   - Add completion status endpoint
   - Update seed data for testing

2. **Phase 2 - Frontend (Future)**
   - Profile completion form
   - Profile editing interface
   - Completion check on login

## Sample Validator Functions

```python
# backend/utils/validators.py

def validate_full_name(name):
    if not name or not isinstance(name, str):
        return False, "Full name is required"
    name = name.strip()
    if len(name) < 1 or len(name) > 100:
        return False, "Full name must be 1-100 characters"
    return True, name

def validate_age(age):
    if not isinstance(age, int):
        return False, "Age must be a number"
    if age < 18 or age > 100:
        return False, "Age must be between 18 and 100"
    return True, age

def validate_languages(languages):
    if not isinstance(languages, list) or len(languages) == 0:
        return False, "At least one language is required"
    if len(languages) > 10:
        return False, "Maximum 10 languages allowed"
    for lang in languages:
        if not isinstance(lang, str) or len(lang) < 2 or len(lang) > 30:
            return False, f"Invalid language: {lang}"
    return True, languages

def validate_rest_days(days):
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if not isinstance(days, list):
        return False, "Rest days must be an array"
    for day in days:
        if day not in valid_days:
            return False, f"Invalid day: {day}"
    return True, days

def validate_skills(skills):
    valid_ratings = ["Basic", "Proficient", "Expert"]
    if not isinstance(skills, list):
        return False, "Skills must be an array"
    if len(skills) > 20:
        return False, "Maximum 20 skills allowed"
    for skill in skills:
        if not isinstance(skill, dict):
            return False, "Each skill must be an object"
        if 'name' not in skill or 'rating' not in skill:
            return False, "Skill must have name and rating"
        if skill['rating'] not in valid_ratings:
            return False, f"Invalid rating: {skill['rating']}"
    return True, skills
```

## Next Steps

1. Create validator utility file
2. Update profile.py API to handle new fields
3. Update firebase_service.py for field defaults
4. Update seed data script
5. Update DATA_SCHEMAS.md documentation
6. Test all endpoints