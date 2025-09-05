<template>
  <div class="login">
    <h1>Login</h1>

    <section class="panel">
      <div class="row">
        <label>Phone Number (+65)</label>
        <input
          v-model="phone"
          type="tel"
          inputmode="numeric"
          pattern="[0-9]*"
          placeholder="91234567"
          aria-label="Singapore phone number without +65"
        />
      </div>
      <div v-if="phone && !isPhoneValid" class="error">Enter 8-digit Singapore number (auto +65 applied)</div>
      <div class="row">
        <label>Password</label>
        <input v-model="password" type="password" placeholder="Password123!" />
      </div>
      <div class="row">
        <button @click="doFirebaseLogin" :disabled="loading || !isPhoneValid || !password">Firebase Sign In</button>
        <button @click="doBackendLogin" :disabled="loading">Backend Login (provision profile)</button>
        <button @click="goTester">Open API Tester</button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="result" class="ok">{{ result }}</div>
    </section>

    <section class="info">
      <p>Tip: After Firebase login, click "Backend Login" to create/update your profile in Firestore via the backend <a href="../services/api.js">/api/auth/login</a>.</p>
      <router-link to="/signup">No account? Sign up</router-link>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { auth, signInWithEmailAndPassword, getIdToken } from '../services/firebase';
import api from '../services/api';
import { formatSingaporePhone, phoneToEmail, emailToPhone } from '../utils/phoneUtils';

const router = useRouter();
const toast = useToast();

const phone = ref('');
const password = ref('');
const error = ref('');
const result = ref('');
const loading = ref(false);
const isPhoneValid = computed(() => {
  try {
    formatSingaporePhone(phone.value);
    return true;
  } catch {
    return false;
  }
});

async function doFirebaseLogin() {
  error.value = '';
  result.value = '';
  loading.value = true;
  try {
    if (!phone.value || !password.value) throw new Error('Phone and password required');
    const formatted = formatSingaporePhone(phone.value);
    const emailAlias = phoneToEmail(formatted);
    const cred = await signInWithEmailAndPassword(auth, emailAlias, password.value);
    result.value = `Firebase login success: ${formatted}`;
    toast.add({ severity: 'success', summary: 'Firebase login success', detail: formatted, life: 3000 });
  } catch (e) {
    let detail = e?.message || String(e);
    const code = e?.code || e?.error?.code;
    if (code === 'auth/user-not-found') {
      detail = 'Phone number not registered. Sign up first.';
    } else if (code === 'auth/wrong-password') {
      detail = 'Incorrect password. Try again.';
    } else if (code === 'auth/too-many-requests') {
      detail = 'Too many attempts. Please wait and try again.';
    } else if (code === 'auth/invalid-email') {
      detail = 'Invalid phone alias generated. Please check the phone number format.';
    }
    error.value = detail;
    toast.add({ severity: 'error', summary: 'Firebase login failed', detail: detail, life: 4000 });
  } finally {
    loading.value = false;
  }
}

async function doBackendLogin() {
  error.value = '';
  result.value = '';
  loading.value = true;
  try {
    const token = await getIdToken(true);
    if (!token) throw new Error('No Firebase ID token. Sign in first.');
    const currentEmail = auth.currentUser?.email || '';
    let inferredPhone = emailToPhone(currentEmail);
    if (!inferredPhone && phone.value) {
      try {
        inferredPhone = formatSingaporePhone(phone.value);
      } catch {}
    }
    const name = auth.currentUser?.displayName || undefined;
    const resp = await api.backendLoginWithIdToken(token, {
      phoneNumber: inferredPhone,
      name,
    });
    const userLabel = resp.data?.user?.phoneNumber || resp.data?.user?.email || resp.data?.user?.uid || 'unknown';
    result.value = `Backend login OK. User: ${userLabel}`;
    toast.add({ severity: 'success', summary: 'Backend login success', detail: userLabel, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    error.value = msg;
    toast.add({ severity: 'error', summary: 'Backend login failed', detail: msg, life: 4000 });
  } finally {
    loading.value = false;
  }
}

function goTester() {
  router.push('/api-tester');
}
</script>

<style scoped>
.login {
  max-width: 540px;
  margin: 30px auto;
  padding: 0 16px 32px 16px;
  text-align: left;
}

.panel {
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 8px;
  background: #fafafa;
}

.row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin: 8px 0;
}

.row label {
  min-width: 100px;
}

.row input {
  flex: 1;
  padding: 6px 8px;
}

.row button {
  padding: 6px 12px;
}

.error {
  color: #b00020;
  font-weight: 600;
  margin-top: 8px;
}

.ok {
  color: #1b5e20;
  font-weight: 600;
  margin-top: 8px;
}

.info {
  margin-top: 16px;
  font-size: 14px;
}
</style>
