<template>
  <div class="signup">
    <h1>Sign Up</h1>
    <div id="recaptcha-container"></div>
    <section class="panel">
      <div>
        <label>Phone Number</label>
        <input v-model="phoneNumber" placeholder="+1234567890" />
        <button @click="sendCode">Send Verification Code</button>
        <input v-model="verificationCode" placeholder="Enter code" />
        <button @click="verifyCode">Verify Code</button>
        <div v-if="successph">{{ successph }}</div>
        <div v-if="errorph" style="color:red">{{ errorph }}</div>
      </div>
      <div class="row">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="you@example.com" />
      </div>
        
      <div class="row">
        <label>Password</label>
        <input v-model="password" type="password" placeholder="Password123!" />
      </div>
      <div class="row">
        <label>Display Name (optional)</label>
        <input v-model="displayName" type="text" placeholder="Your name" />
      </div>
      <div class="row">
        <button @click="doFirebaseSignUp" :disabled="loading">Create Firebase Account</button>
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
import { ref, onMounted, nextTick} from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { auth, createUserWithEmailAndPassword, getIdToken,  } from '../services/firebase';
import { updateProfile, signInWithPhoneNumber, RecaptchaVerifier } from 'firebase/auth';
import api from '../services/api';

const router = useRouter();
const toast = useToast();

const email = ref('');
const password = ref('');
const displayName = ref('');
const error = ref('');
const result = ref('');
const loading = ref(false);

const phoneNumber = ref('');
const verificationCode = ref('');
const confirmationResult = ref(null);
const errorph = ref('');
const successph = ref('');
const user = ref(null); // <- Track the authenticated user

onMounted(async () => {
  await nextTick();
  const container = document.getElementById('recaptcha-container');
  if (container && !window.recaptchaVerifier) {
    window.recaptchaVerifier = new RecaptchaVerifier('recaptcha-container', {
      size: 'invisible',
      callback: () => {
        console.log('reCAPTCHA solved');
      },
      'expired-callback': () => {
        console.log('reCAPTCHA expired, resetting');
      }
    }, auth);
    try {
      await window.recaptchaVerifier.render();
    } catch (e) {
      console.warn('reCAPTCHA render failed:', e.message);
    }
  }
});


async function verifyCode() {
  errorph.value = '';
  try {
    if (!confirmationResult.value) {
      errorph.value = 'Please request a verification code first.';
      return;
    }
    const result = await confirmationResult.value.confirm(verificationCode.value);

    user.value = result.user; // <- Authenticated user (phone-based)
    successph.value = `Phone sign-in successful: ${user.value.phoneNumber}`;
    toast.add({
      severity: 'success',
      summary: 'Phone Sign-in Successful',
      detail: user.value.phoneNumber,
      life: 3000
    });

    // Optional: Update display name if provided
    if (displayName.value) {
      await updateProfile(user.value, { displayName: displayName.value });
    }

  } catch (e) {
    errorph.value = e.message;
  }
}

async function sendCode() {
  errorph.value = '';
  successph.value = '';
  
  if (!phoneNumber.value) {
    errorph.value = 'Please enter a valid phone number.';
    return;
  }

  try {
    confirmationResult.value = await signInWithPhoneNumber(auth, phoneNumber.value, window.recaptchaVerifier);
    successph.value = 'Verification code sent!';
    toast.add({
      severity: 'success',
      summary: 'Code Sent',
      detail: phoneNumber.value,
      life: 3000
    });
  } catch (e) {
    errorph.value = e.message;
    console.error('Error sending SMS:', e);
  }
}


async function doFirebaseSignUp() {
  error.value = '';
  result.value = '';
  loading.value = true;
  try {
    // if user already signed in via phone, skip email sign-up
    if (user.value) {
      result.value = `Phone sign-in complete: ${user.value.phoneNumber}`;
      return;  // <-- Prevents creating email/password account if phone sign-in done
    }

    if (!email.value || !password.value) throw new Error('Email and password required');
    const cred = await createUserWithEmailAndPassword(auth, email.value, password.value);
    if (displayName.value) {
      try {
        await updateProfile(cred.user, { displayName: displayName.value });
      } catch (e) {
        console.warn('updateProfile failed:', e);
      }
    }
    result.value = `Sign up success: ${cred.user.email}`;
    toast.add({ severity: 'success', summary: 'Sign up success', detail: cred.user.email, life: 3000 });
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