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
app.use(router);
app.mount('#app');
