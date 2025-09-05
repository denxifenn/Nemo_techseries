import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import ToastService from 'primevue/toastservice';

import App from './App.vue';
import router from './router';
import api from './services/api';
import { onAuth, getIdToken } from './services/firebase';

const app = createApp(App);

app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
});
app.use(ToastService);
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
