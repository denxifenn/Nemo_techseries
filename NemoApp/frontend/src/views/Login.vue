<template>
    <div class="login-container">
        <div class="login-box">
            <h1 class="login-header">Login To Your Account!</h1>
            <div>
                <!-- Keep incoming UI/UX, wire to backend auth -->
                <section class="auth-field">
                    <InputText
                        v-model="phone"
                        type="text"
                        placeholder="Phone Number"
                        class="auth-input-username"
                    />
                    <Password
                        v-model="password"
                        type="text"
                        placeholder="Password"
                        :feedback="false"
                        toggleMask
                        fluid
                        class="auth-input-password"
                    />
                </section>

                <div class="buttons">
                    <Button
                        type="button"
                        severity="secondary"
                        label="Login"
                        class="auth-login-btn"
                        @click="handleLogin"
                    />
                    <Button
                        type="button"
                        severity="secondary"
                        label="Sign Up"
                        class="auth-signup-btn"
                        @click="handleSignup"
                    />
                </div>
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

import { auth, signInWithEmailAndPassword, getIdToken } from '../services/firebase';
import api from '../services/api';
import { formatSingaporePhone, phoneToEmail } from '../utils/phoneUtils';

const router = useRouter();
const toast = useToast();

const phone = ref('');
const password = ref('');

async function handleLogin() {
  try {
    if (!phone.value || !password.value) {
      throw new Error('Phone and password required');
    }
    const formatted = formatSingaporePhone(phone.value);
    const emailAlias = phoneToEmail(formatted);

    await signInWithEmailAndPassword(auth, emailAlias, password.value);

    // Backend login/provisioning with Firebase ID token
    const token = await getIdToken(true);
    if (!token) throw new Error('No Firebase ID token. Sign in first.');
    const name = auth.currentUser?.displayName || undefined;

    await api.backendLoginWithIdToken(token, { phoneNumber: formatted, name });

    toast.add({ severity: 'success', summary: 'Login success', detail: formatted, life: 3000 });
    try { router.push('/discover'); } catch {}
  } catch (e) {
    let detail = e?.response?.data?.error || e?.message || String(e);
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
    toast.add({ severity: 'error', summary: 'Login failed', detail, life: 4000 });
  }
}

function handleSignup() {
  router.push({ name: 'SignUp' });
}
</script>

<style scoped>
/* Preserve incoming design */
.login-container { 
    background-image: url('@/assets/workers_background.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    min-height: 100vh;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.auth-input-username {
    width: 100%;
    min-height: 2.5rem;
    font-size: 1rem;
    box-sizing: border-box;
    margin-top: 3rem;
    margin-left: 0.2rem;
}

.auth-input-password {
    margin-top: 3rem;
    width: 100%;
    min-height: 2.5rem;
    font-size: 1rem;
    box-sizing: border-box;
    margin-left: 0.2rem;
}

.auth-login-btn {
    margin-top: 3rem;
    width: 8rem;
    height: 4rem;
    color: black;
    background: #FFC67B;
    font-family: 'Poppins', sans-serif;
    margin-right: 0.5rem;
}

.login-header {
    color: #1c1102; 
    text-align: center;
    font-size: 2rem;
    font-family: 'Poppins', sans-serif;
    margin-top: 1rem;
}

.login-box {
    background-color: white;
    padding: 5rem;
    border-radius: 8px;
    width: 600px;
    display: flex;
    height: 700px;
    flex-direction: column;
    align-items: center;
    margin-left: 50px;  
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.auth-signup-btn {
    margin-top: 1rem;
    width: 8rem;
    height: 4rem;
    color: rgb(255, 255, 255);
    background: #ffa114;
    font-family: 'Poppins', sans-serif;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
</style>
