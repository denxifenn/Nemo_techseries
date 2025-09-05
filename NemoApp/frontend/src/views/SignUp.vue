<template>
  <div class="signup">
    <h1>Sign Up</h1>

    <section class="panel">
      <div class="row">
        <label>Phone Number (+65)</label>
        <input v-model="phone" type="tel" placeholder="91234567" />
      </div>
      <div v-if="phone && !isPhoneValid" class="error">Enter 8-digit Singapore number</div>
      <div class="row">
        <label>Password</label>
        <input v-model="password" type="password" placeholder="Password123!" />
      </div>
      <div class="row">
        <label>Display Name (optional)</label>
        <input v-model="displayName" type="text" placeholder="Your name" />
      </div>
      <div class="row">
        <button @click="doFirebaseSignUp" :disabled="loading || !isPhoneValid || !password">Create Firebase Account</button>
        <button @click="doBackendLogin" :disabled="loading">Backend Login (provision profile)</button>
        <button @click="goTester">Open API Tester</button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="result" class="ok">{{ result }}</div>
    </section>

    <section class="info">
      <p>
        After creating an account, click "Backend Login" to create your user profile in Firestore
        through the backend <a href="../services/api.js">/api/auth/login</a>.
      </p>
      <router-link to="/login">Already have an account? Log in</router-link>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { auth, createUserWithEmailAndPassword, getIdToken } from '../services/firebase';
import { updateProfile } from 'firebase/auth';
import api from '../services/api';
import { formatSingaporePhone, phoneToEmail, emailToPhone } from '../utils/phoneUtils';

const router = useRouter();
const toast = useToast();

const phone = ref('');
const password = ref('');
const displayName = ref('');
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

async function doFirebaseSignUp() {
  error.value = '';
  result.value = '';
  loading.value = true;
  try {
    if (!phone.value || !password.value) throw new Error('Phone and password required');
    const formatted = formatSingaporePhone(phone.value);
    const emailAlias = phoneToEmail(formatted);
    const cred = await createUserWithEmailAndPassword(auth, emailAlias, password.value);
    if (displayName.value) {
      try {
        await updateProfile(cred.user, { displayName: displayName.value });
      } catch (e) {
        console.warn('updateProfile failed:', e);
      }
    }
    result.value = `Sign up success: ${formatted}`;
    toast.add({ severity: 'success', summary: 'Sign up success', detail: formatted, life: 3000 });
  } catch (e) {
    const msg = e?.message || String(e);
    error.value = msg;
    toast.add({ severity: 'error', summary: 'Sign up failed', detail: msg, life: 4000 });
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
    const name = auth.currentUser?.displayName || (displayName.value || '').trim() || undefined;
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
.signup {
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
  min-width: 120px;
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