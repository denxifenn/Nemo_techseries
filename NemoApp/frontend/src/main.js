import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import ToastService from 'primevue/toastservice';
import Ripple from 'primevue/ripple';
import 'primeicons/primeicons.css';

import App from './App.vue';
import router from './router';
import api from './services/api';
import { onAuth, getIdToken } from './services/firebase';

// Pinia store (global state)
import { pinia } from './stores';
import { useAuthStore } from './stores/auth';
import { onAuth } from './services/firebase';

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

// Initialize auth once before installing router to reduce guard flicker
const auth = useAuthStore();
auth.initializeAuth();

// Subscribe to Firebase auth changes to keep store in sync
onAuth(async (fbUser) => {
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

// Auto-provision Firestore user profile via backend when authenticated
onAuth(async (user) => {
  if (user) {
    try {
      const token = await getIdToken(true);
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
