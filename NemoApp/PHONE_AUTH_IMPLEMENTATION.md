# Phone Number Authentication Implementation Plan

## Overview
This document outlines the implementation strategy for converting the authentication system from email+password to phone+password using Firebase's email/password authentication as the underlying mechanism.

## Approach: Phone-to-Email Conversion

Since Firebase phone authentication requires SMS/OTP verification (which requires payment), we'll use a workaround:
- Store phone numbers as emails in Firebase Auth
- Convert phone numbers to a special email format: `{phone}@phone.local`
- Store the actual phone number in Firestore user documents

## Phone Number Format

### Singapore Phone Number Rules:
- Accept 8-digit Singapore numbers (e.g., "91234567")
- Auto-prepend "+65" country code
- Accept numbers with "+65" prefix already included
- Valid formats:
  - `91234567` → `+6591234567`
  - `+6591234567` → `+6591234567`
  - `6591234567` → `+6591234567`

### Email Conversion Pattern:
- Phone: `+6591234567`
- Firebase Email: `6591234567@phone.local`
- Remove "+" from email to avoid issues

## Implementation Architecture

### Frontend Components

#### 1. Phone Number Utilities (`/frontend/src/utils/phoneUtils.js`)
```javascript
// Validate Singapore phone number
function isValidSingaporePhone(phone)

// Format phone number with +65 prefix
function formatSingaporePhone(phone)

// Convert phone to email format for Firebase
function phoneToEmail(phone)

// Convert email back to phone format
function emailToPhone(email)

// Check if email is a phone-based email
function isPhoneEmail(email)
```

#### 2. Updated Components
- **SignUp.vue**: Replace email field with phone field
- **Login.vue**: Replace email field with phone field
- Both components will:
  - Validate Singapore phone numbers
  - Auto-format with +65 prefix
  - Convert to email format before Firebase calls

### Backend Components

#### 1. Phone Number Utilities (`/backend/utils/phone_utils.py`)
```python
def is_valid_singapore_phone(phone: str) -> bool
def format_singapore_phone(phone: str) -> str
def phone_to_email(phone: str) -> str
def email_to_phone(email: str) -> str
def is_phone_email(email: str) -> bool
```

#### 2. Updated Services
- **firebase_service.py**: 
  - Handle phone-to-email conversion
  - Store actual phone number in Firestore
  - Support both email and phone authentication

- **auth.py**:
  - Accept phone number in login/signup
  - Convert to email format for Firebase

### Database Schema Updates

#### Firestore User Document
```javascript
{
  uid: "...",
  email: "6591234567@phone.local",  // Firebase email format
  phoneNumber: "+6591234567",       // Actual phone number
  name: "...",
  role: "user",
  profilePicture: "",
  friends: [],
  createdAt: timestamp
}
```

## Migration Strategy

### For New Users:
1. Enter phone number in signup form
2. System auto-adds +65 prefix
3. Converts to email format for Firebase Auth
4. Stores actual phone in Firestore

### For Existing Users:
- Create migration script to handle existing email-based users
- They can continue using email login
- Or optionally migrate to phone authentication

## Security Considerations

1. **Phone Number Privacy**: Store hashed phone numbers if needed
2. **Validation**: Strict validation of Singapore phone numbers
3. **Rate Limiting**: Implement rate limiting for authentication attempts
4. **Domain Suffix**: Use `.local` domain to prevent email conflicts

## Testing Checklist

- [ ] Phone number validation (various formats)
- [ ] Auto-prefix functionality
- [ ] Signup with phone number
- [ ] Login with phone number
- [ ] Backend token verification
- [ ] Firestore user document creation
- [ ] Error handling for invalid numbers
- [ ] Migration of existing users

## Implementation Steps

1. **Phase 1: Utilities**
   - Create phone number utility functions
   - Test conversion logic

2. **Phase 2: Frontend**
   - Update SignUp.vue
   - Update Login.vue
   - Test UI changes

3. **Phase 3: Backend**
   - Update firebase_service.py
   - Update auth.py
   - Test API endpoints

4. **Phase 4: Migration**
   - Create migration script
   - Test with sample data

5. **Phase 5: Documentation**
   - Update API documentation
   - Update user guides

## Sample Code Flow

### Signup Flow:
```
User Input: "91234567" + password
→ Frontend formats: "+6591234567"
→ Convert to email: "6591234567@phone.local"
→ Firebase createUser("6591234567@phone.local", password)
→ Firestore stores: { phoneNumber: "+6591234567", email: "6591234567@phone.local" }
```

### Login Flow:
```
User Input: "91234567" + password
→ Frontend formats: "+6591234567"
→ Convert to email: "6591234567@phone.local"
→ Firebase signIn("6591234567@phone.local", password)
→ Get ID token
→ Backend verifies token and returns user data
```

## Notes

- The `.local` domain is reserved for local use and won't conflict with real emails
- This approach maintains Firebase security while avoiding SMS costs
- Users won't see the email format - it's hidden in the implementation