import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import ToastService from 'primevue/toastservice';
import Ripple from 'primevue/ripple';
import 'primeicons/primeicons.css';

import App from './App.vue';
import router from './router';

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
  // Signal router guards that Firebase has emitted its first state
  try {
    if (typeof auth.markAuthReady === 'function') {
      auth.markAuthReady();
    }
  } catch (_) { /* no-op */ }

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
app.mount('#app');
