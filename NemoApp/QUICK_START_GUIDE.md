# Nemo App - Quick Start Guide

## Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- Firebase account (free tier is sufficient)
- Git

## Step 1: Firebase Setup

### 1.1 Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Name it "nemo-app" 
4. Disable Google Analytics (not needed for MVP)
5. Click "Create project"

### 1.2 Enable Services
1. **Authentication**:
   - Go to Authentication > Sign-in method
   - Enable "Email/Password"

2. **Firestore Database**:
   - Go to Firestore Database
   - Click "Create database"
   - Choose "Start in test mode" (for development)
   - Select your region (asia-southeast1 for Singapore)

3. **Get Configuration**:
   - Go to Project Settings > General
   - Scroll to "Your apps" > Click "Web" icon
   - Register app with nickname "nemo-web"
   - Copy the configuration object

### 1.3 Get Admin SDK Key
1. Go to Project Settings > Service accounts
2. Click "Generate new private key"
3. Save as `firebase-admin-key.json` in `NemoApp/firebase/`

## Step 2: Backend Setup

### 2.1 Install Dependencies
```bash
cd NemoApp/backend
pip install -r requirements.txt
```

### 2.2 Update requirements.txt
```txt
Flask==3.0.0
Flask-CORS==4.0.0
Flask-RESTful==0.3.10
firebase-admin==6.1.0
python-dotenv==1.0.0
```

### 2.3 Create .env file
```bash
# backend/.env
FIREBASE_PROJECT_ID=nemo-app
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 2.4 Update app.py
```python
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Import and register blueprints
    from api.auth import auth_bp
    from api.events import events_bp
    from api.bookings import bookings_bp
    from api.profile import profile_bp
    from api.friends import friends_bp
    from api.admin import admin_bp
    from api.suggestions import suggestions_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(suggestions_bp)
    
    @app.route('/')
    def index():
        return {'message': 'Nemo API is running!'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```

## Step 3: Frontend Setup

### 3.1 Install Vue CLI (if not installed)
```bash
npm install -g @vue/cli
```

### 3.2 Create Vue Project
```bash
cd NemoApp
vue create frontend
# Choose: Vue 3, Router, Pinia
```

### 3.3 Install Additional Dependencies
```bash
cd frontend
npm install axios firebase bootstrap-vue-3 @fortawesome/fontawesome-free
```

### 3.4 Update package.json
```json
{
  "name": "nemo-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "serve": "vue-cli-service serve",
    "build": "vue-cli-service build",
    "lint": "vue-cli-service lint"
  },
  "dependencies": {
    "axios": "^1.4.0",
    "bootstrap": "^5.3.0",
    "bootstrap-vue-3": "^0.5.1",
    "firebase": "^10.5.0",
    "pinia": "^2.1.6",
    "vue": "^3.3.4",
    "vue-router": "^4.2.4"
  },
  "devDependencies": {
    "@vue/cli-plugin-router": "~5.0.0",
    "@vue/cli-service": "~5.0.0"
  }
}
```

### 3.5 Configure Firebase in Frontend
```javascript
// frontend/src/services/firebase.js
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  // Paste your config from Firebase Console here
  apiKey: "your-api-key",
  authDomain: "nemo-app.firebaseapp.com",
  projectId: "nemo-app",
  storageBucket: "nemo-app.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

## Step 4: Create Basic Project Structure

### 4.1 Backend Structure
```bash
backend/
├── api/
│   ├── __init__.py
│   ├── auth.py
│   ├── events.py
│   ├── bookings.py
│   ├── profile.py
│   ├── friends.py
│   ├── admin.py
│   └── suggestions.py
├── services/
│   ├── __init__.py
│   └── firebase_service.py
├── utils/
│   ├── __init__.py
│   └── decorators.py
├── .env
├── app.py
└── requirements.txt
```

### 4.2 Frontend Structure
```bash
frontend/src/
├── assets/
│   └── styles/
│       └── main.css
├── components/
│   ├── common/
│   │   ├── NavBar.vue
│   │   └── LoadingSpinner.vue
│   ├── events/
│   │   ├── EventCard.vue
│   │   └── EventList.vue
│   └── modals/
│       ├── BookingModal.vue
│       └── GroupBookingModal.vue
├── router/
│   └── index.js
├── services/
│   ├── api.js
│   ├── auth.js
│   └── firebase.js
├── stores/
│   ├── auth.js
│   └── events.js
├── views/
│   ├── HomePage.vue
│   ├── LoginPage.vue
│   ├── RegisterPage.vue
│   ├── EventsPage.vue
│   ├── EventDetailsPage.vue
│   ├── ProfilePage.vue
│   ├── FriendsPage.vue
│   └── AdminPage.vue
├── App.vue
└── main.js
```

## Step 5: Run the Application

### Terminal 1: Backend
```bash
cd NemoApp/backend
python app.py
# Server runs on http://localhost:5000
```

### Terminal 2: Frontend
```bash
cd NemoApp/frontend
npm run serve
# App runs on http://localhost:8080
```

## Step 6: Test Basic Setup

1. Open browser to http://localhost:8080
2. You should see the Vue app
3. Open http://localhost:5000
4. You should see: {"message": "Nemo API is running!"}

## Common Issues & Solutions

### Issue: Firebase Admin SDK not working
**Solution**: Make sure `firebase-admin-key.json` is in the correct location and not committed to git

### Issue: CORS errors
**Solution**: Ensure Flask-CORS is installed and configured in app.py

### Issue: Port already in use
**Solution**: Change port in `.env` file or use different port

### Issue: Firebase authentication not working
**Solution**: Check Firebase Console > Authentication is enabled

## Next Steps

1. **Implement Authentication Flow**:
   - Start with KAN-7 (Login API)
   - Then KAN-14 (Login Page)
   - Then KAN-15 (Register Page)

2. **Create Database Collections**:
   - Follow KAN-27 to KAN-32
   - Use Firebase Console or create programmatically

3. **Build Core Features**:
   - Events listing (KAN-4, KAN-8)
   - Event details (KAN-13)
   - Booking system (KAN-9, KAN-10, KAN-11)

## Development Tips

1. **Use Firebase Emulator** for local development:
   ```bash
   npm install -g firebase-tools
   firebase init emulators
   firebase emulators:start
   ```

2. **API Testing**: Use Postman or Thunder Client (VS Code extension)

3. **Vue DevTools**: Install browser extension for debugging

4. **Hot Reload**: Both Flask and Vue support hot reload in development

5. **Version Control**: 
   ```bash
   # .gitignore
   .env
   firebase-admin-key.json
   node_modules/
   __pycache__/
   *.pyc
   .DS_Store
   ```

## Useful Commands

```bash
# Backend
pip freeze > requirements.txt  # Update dependencies
python -m pytest  # Run tests

# Frontend
npm run build  # Build for production
npm run lint  # Check code style

# Firebase
firebase deploy --only hosting  # Deploy frontend
firebase deploy --only firestore:rules  # Deploy security rules
```

## Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Bootstrap Vue 3](https://bootstrap-vue-3.github.io/bootstrap-vue-3/)

## Support

For questions about implementation:
1. Check the `JIRA_TASKS_IMPLEMENTATION.md` for detailed code examples
2. Review `MVP_IMPLEMENTATION_PLAN.md` for architecture decisions
3. Consult `ARCHITECTURE_PLAN.md` for system design

Ready to start coding! Begin with Step 1 and work through systematically. Good luck! 🚀