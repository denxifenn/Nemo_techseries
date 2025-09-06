import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import ToastService from 'primevue/toastservice';
import Ripple from 'primevue/ripple';
import 'primeicons/primeicons.css';

import App from './App.vue';
import router from './router';
import api from './services/api';

// Firebase services
import { onAuth, getIdToken } from './services/firebase';

// Pinia store (global state)
import { pinia } from './stores';
import { useAuthStore } from './stores/auth';

const app = createApp(App);

app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
});
app.use(ToastService);
app.directive('ripple', Ripple);

// Install Pinia before router so guards can access the store
app.use(pinia);
console.debug('[main] Pinia installed');

// Initialize auth once before installing router to reduce guard flicker
const auth = useAuthStore();
console.debug('[main] initializeAuth: invoked at app bootstrap (not awaited)');
auth.initializeAuth();

// Subscribe to Firebase auth changes to keep store in sync
onAuth(async (fbUser) => {
  console.debug('[main] onAuth(1):', fbUser ? `signed-in uid=${fbUser.uid}` : 'signed-out');
  if (fbUser) {
    // Refresh local profile if user object exists
    await auth.fetchProfile();
    auth.isAuthenticated = true;
    auth.isAdmin = (auth.user?.role === 'admin');
    await auth.checkProfileCompletion();
  } else {
    // User signed out in Firebase → clear only local session
    auth.clearSessionLocal();
  }
});

app.use(router);
console.debug('[main] Router installed');

// Auto-provision Firestore user profile via backend when authenticated
onAuth(async (user) => {
  console.debug('[main] onAuth(2): provisioning handler', user ? `uid=${user.uid}` : 'no user');
  if (user) {
    try {
      const token = await getIdToken(true);
      console.debug('[main] provisioning: got token?', !!token);
      if (token) {
        await api.backendLoginWithIdToken(token);
        console.log('[provision] ensured Firestore user doc for', user.uid);
      }
    } catch (e) {
      console.warn('[provision] backend provisioning failed:', e?.response?.data?.error || e?.message || e);
    }
  }
});

app.mount('#app');
