<template>
  <div class="signup-container">
    <div class="signup-box">
      <h1 class="signup-header">SIGN UP FOR AN ACCOUNT!</h1>
      <div class="card flex justify-center">
        <section class="flex flex-col gap-4 w-full sm:w-80">
          <!-- User Inputs -->
          <InputText v-model="firstName" type="text" placeholder="First Name" class="first-name-btn" />
          <InputText v-model="lastName" type="text" placeholder="Last Name" class="last-name-btn" />
          <InputText v-model="phone" type="text" placeholder="Phone Number (+65...)" class="phone-number-btn" />
          <InputText v-model="fin" type="text" placeholder="FIN Number" maxlength="9" class="FIN-number-btn" />

          <!-- SMS Verification -->
          <Button label="Send Verification Code" class="submit-btn" @click="sendCode" />
          <InputText v-model="verificationCode" type="text" placeholder="Enter SMS Code" />
          <Button label="Verify Code" class="submit-btn" @click="verifyCode" />

          <!-- Password & Signup -->
          <Password
            v-model="password"
            placeholder="Password"
            :feedback="false"
            toggleMask
            class="password-btn"
          />
          <Button
            type="button"
            severity="secondary"
            label="Create Account"
            style="background-color: #ffa690; color: black; font-weight: bold;"
            class="submit-btn"
            :disabled="loading"
            @click="handleSignUp"
          />

          <!-- Feedback -->
          <div v-if="error" class="error">{{ error }}</div>
          <div v-if="result" class="ok">{{ result }}</div>
          <div v-if="successph" class="ok">{{ successph }}</div>
          <div v-if="errorph" class="error">{{ errorph }}</div>
        </section>
      </div>
    </div>

    <div id="recaptcha-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';

import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';

import { auth, createUserWithEmailAndPassword, getIdToken } from '../services/firebase';
import { updateProfile, signInWithPhoneNumber, RecaptchaVerifier } from 'firebase/auth';

import api from '../services/api';
import { formatSingaporePhone, phoneToEmail } from '../utils/phoneUtils';

const router = useRouter();
const toast = useToast();

// Refs
const firstName = ref('');
const lastName = ref('');
const phone = ref('');
const fin = ref('');
const password = ref('');
const verificationCode = ref('');
const confirmationResult = ref(null);
const successph = ref('');
const errorph = ref('');
const error = ref('');
const result = ref('');
const loading = ref(false);
const user = ref(null); // Authenticated user (after phone verification)

// Init reCAPTCHA
onMounted(async () => {
  await nextTick();
  const container = document.getElementById('recaptcha-container');
  if (container && !window.recaptchaVerifier) {
    window.recaptchaVerifier = new RecaptchaVerifier('recaptcha-container', {
      size: 'invisible',
      callback: () => console.log('reCAPTCHA solved'),
      'expired-callback': () => console.log('reCAPTCHA expired'),
    }, auth);
    try {
      await window.recaptchaVerifier.render();
    } catch (e) {
      console.warn('reCAPTCHA render failed:', e.message);
    }
  }
});

// Send verification SMS
async function sendCode() {
  errorph.value = '';
  successph.value = '';
  const formatted = formatSingaporePhone(phone.value);

  if (!formatted) {
    errorph.value = 'Please enter a valid Singapore phone number.';
    return;
  }

  try {
    confirmationResult.value = await signInWithPhoneNumber(auth, formatted, window.recaptchaVerifier);
    successph.value = 'Verification code sent!';
    toast.add({ severity: 'success', summary: 'Code Sent', detail: formatted, life: 3000 });
  } catch (e) {
    errorph.value = e.message;
    console.error('Error sending SMS:', e);
  }
}

// Verify code
async function verifyCode() {
  errorph.value = '';
  try {
    if (!confirmationResult.value) {
      errorph.value = 'Please request a verification code first.';
      return;
    }
    const result = await confirmationResult.value.confirm(verificationCode.value);
    user.value = result.user;
    successph.value = `Phone verification successful: ${user.value.phoneNumber}`;
    toast.add({ severity: 'success', summary: 'Verified', detail: user.value.phoneNumber, life: 3000 });

    // Optional: update name if available
    const displayName = `${(firstName.value || '').trim()} ${(lastName.value || '').trim()}`.trim();
    if (displayName) {
      await updateProfile(user.value, { displayName });
    }
  } catch (e) {
    errorph.value = e.message;
  }
}

// Full sign-up
async function handleSignUp() {
  error.value = '';
  result.value = '';
  loading.value = true;

  try {
    const formatted = formatSingaporePhone(phone.value);
    const emailAlias = phoneToEmail(formatted);
    const finNum = (fin.value || '').trim().toUpperCase();

    if (!user.value) {
      throw new Error('Please verify your phone number first.');
    }

    if (!password.value) throw new Error('Password is required.');
    if (finNum.length !== 9) throw new Error('FIN must be 9 characters.');

    const cred = await createUserWithEmailAndPassword(auth, emailAlias, password.value);

    const displayName = `${(firstName.value || '').trim()} ${(lastName.value || '').trim()}`.trim();
    if (displayName) {
      try {
        await updateProfile(cred.user, { displayName });
      } catch (e) {
        console.warn('updateProfile failed:', e);
      }
    }

    const token = await getIdToken(true);
    if (!token) throw new Error('No Firebase ID token available.');

    const resp = await api.backendLoginWithIdToken(token, {
      phoneNumber: formatted,
      name: displayName || undefined,
      finNumber: finNum,
    });

    const userLabel = resp.data?.user?.phoneNumber || resp.data?.user?.uid || 'unknown';
    result.value = `Account created and provisioned: ${userLabel}`;
    toast.add({ severity: 'success', summary: 'Account Created', detail: userLabel, life: 3000 });

    try {
      router.push('/discover');
    } catch {}
  } catch (e) {
    let msg = e?.response?.data?.error || e?.message || String(e);
    const code = e?.code || '';
    if (code === 'auth/email-already-in-use' || msg.includes('auth/email-already-in-use')) {
      msg = 'Phone number already in use.';
    }

    error.value = msg;
    toast.add({ severity: 'error', summary: 'Sign up failed', detail: msg, life: 4000 });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
/* Same styles as previous UI version */
.signup-container {
  background-image: url("@/assets/workers_background.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.signup-box {
  background-color: #ffa600;
  padding: 5rem;
  border-radius: 8px;
  width: 700px;
  display: flex;
  height: 800px;
  flex-direction: column;
  align-items: center;
  margin-left: 50px;
}

.signup-header {
  font-family: "archivo black, sans-serif";
  font-size: 2.5rem;
  color: rgb(255, 255, 255);
  margin-bottom: 2rem;
  text-align: center;
}

.first-name-btn, .last-name-btn, .phone-number-btn, .FIN-number-btn, .password-btn {
  width: 100%;
  min-height: 2.5rem;
  font-size: 1rem;
  box-sizing: border-box;
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.submit-btn {
  color: #ffc67b;
  font-family: "Poppins", "sans-serif";
  width: 50%;
  margin-right: 0.5rem;
  margin-top: 10%;
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
</style>
