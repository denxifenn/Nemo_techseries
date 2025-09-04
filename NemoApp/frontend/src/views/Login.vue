<template>
  <div class="login">
    <h1>Login</h1>

    <section class="panel">
      <div class="row">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="you@example.com" />
      </div>
      <div class="row">
        <label>Password</label>
        <input v-model="password" type="password" placeholder="Password123!" />
      </div>
      <div class="row">
        <button @click="doFirebaseLogin" :disabled="loading">Firebase Sign In</button>
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { auth, signInWithEmailAndPassword, getIdToken } from '../services/firebase';
import api from '../services/api';

const router = useRouter();
const toast = useToast();

const email = ref('');
const password = ref('');
const error = ref('');
const result = ref('');
const loading = ref(false);

async function doFirebaseLogin() {
  error.value = '';
  result.value = '';
  loading.value = true;
  try {
    if (!email.value || !password.value) throw new Error('Email and password required');
    const cred = await signInWithEmailAndPassword(auth, email.value, password.value);
    result.value = `Firebase login success: ${cred.user.email}`;
    toast.add({ severity: 'success', summary: 'Firebase login success', detail: cred.user.email, life: 3000 });
  } catch (e) {
    const msg = e?.message || String(e);
    error.value = msg;
    toast.add({ severity: 'error', summary: 'Firebase login failed', detail: msg, life: 4000 });
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
    const resp = await api.backendLoginWithIdToken(token);
    const userLabel = resp.data?.user?.email || resp.data?.user?.uid || 'unknown';
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
