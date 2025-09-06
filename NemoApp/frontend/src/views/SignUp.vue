<template>
  <div class="signup-container">
    <div class="signup-box">
      <h1 class="signup-header">SIGN UP FOR AN ACCOUNT!</h1>
      <div class="card flex justify-center">
        <section class="flex flex-col gap-4 w-full sm:w-80">
          <InputText
            v-model="firstName"
            type="text"
            placeholder="First Name"
            class="first-name-btn"
          />
          <InputText
            v-model="lastName"
            type="text"
            placeholder="Last Name"
            class="last-name-btn"
          />
          <InputText
            v-model="phone"
            type="text"
            placeholder="Phone Number"
            class="phone-number-btn"
          />
          <InputText
            v-model="fin"
            type="text"
            placeholder="FIN Number"
            maxlength="9"
            class="FIN-number-btn"
          />
          <Password
            v-model="password"
            type="text"
            placeholder="Password"
            :feedback="false"
            toggleMask
            fluid
            class="password-btn"
          />
          <Button
            type="button"
            severity="secondary"
            label="Sign Up"
            style="background-color: #ffa690; color: black; font-weight: bold;"
            class="submit-btn"
            @click="handleSignUp"
          />
          <div v-if="error" class="error">{{ error }}</div>
          <div v-if="result" class="ok">{{ result }}</div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';

import { auth, createUserWithEmailAndPassword, getIdToken } from '../services/firebase';
import { updateProfile } from 'firebase/auth';
import api from '../services/api';
import { formatSingaporePhone, phoneToEmail } from '../utils/phoneUtils';

const router = useRouter();
const toast = useToast();

const firstName = ref('');
const lastName = ref('');
const phone = ref('');
const fin = ref('');
const password = ref('');

const error = ref('');
const result = ref('');
const loading = ref(false);

async function handleSignUp() {
  error.value = '';
  result.value = '';
  loading.value = true;
  try {
    if (!phone.value || !password.value || !fin.value) {
      throw new Error('Phone, FIN and password required');
    }
    const formatted = formatSingaporePhone(phone.value);
    const emailAlias = phoneToEmail(formatted);
    const finNum = (fin.value || '').trim().toUpperCase();
    if (finNum.length !== 9) {
      throw new Error('FIN must be 9 characters');
    }

    const cred = await createUserWithEmailAndPassword(auth, emailAlias, password.value);

    // Optional display name update
    const displayName = `${(firstName.value || '').trim()} ${(lastName.value || '').trim()}`.trim();
    if (displayName) {
      try {
        await updateProfile(cred.user, { displayName });
      } catch (e) {
        console.warn('updateProfile failed:', e);
      }
    }

    // Backend provisioning
    const token = await getIdToken(true);
    if (!token) throw new Error('No Firebase ID token after signup.');
    const resp = await api.backendLoginWithIdToken(token, {
      phoneNumber: formatted,
      name: displayName || undefined,
      finNumber: finNum,
    });

    const userLabel = resp.data?.user?.phoneNumber || resp.data?.user?.uid || 'unknown';
    result.value = `Account created and provisioned: ${userLabel}`;
    toast.add({ severity: 'success', summary: 'Account created', detail: userLabel, life: 3000 });

    try { router.push('/discover'); } catch {}
  } catch (e) {
    let msg = e?.response?.data?.error || e?.message || String(e);

    // Map Firebase duplicate email (email alias from phone) to user-friendly phone message
    const code = e?.code || '';
    if (code === 'auth/email-already-in-use' || String(msg).includes('auth/email-already-in-use')) {
      msg = 'Phone number already in use';
    }

    error.value = msg;
    toast.add({ severity: 'error', summary: 'Sign up failed', detail: msg, life: 4000 });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
/* Incoming design preserved */
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

.first-name-btn {
  width: 100%;
  min-height: 2.5rem;
  font-size: 1rem;
  box-sizing: border-box;
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.last-name-btn {
  width: 100%;
  min-height: 2.5rem;
  font-size: 1rem;
  box-sizing: border-box;
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.phone-number-btn {
  width: 100%;
  min-height: 2.5rem;
  font-size: 1rem;
  box-sizing: border-box;
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.FIN-number-btn {
  width: 100%;
  min-height: 2.5rem;
  font-size: 1rem;
  box-sizing: border-box;
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.password-btn {
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
