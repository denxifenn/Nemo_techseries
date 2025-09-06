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

// Use centralized auth store
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const toast = useToast();
const auth = useAuthStore();

const phone = ref('');
const password = ref('');

async function handleLogin() {
  try {
    if (!phone.value || !password.value) {
      throw new Error('Phone and password required');
    }

    const result = await auth.login(phone.value, password.value);
    if (!result?.success) {
      throw new Error(result?.error || 'Login failed');
    }

    toast.add({ severity: 'success', summary: 'Login success', detail: phone.value, life: 3000 });

    // If profile not completed, force completion flow
    if (auth.needsProfileCompletion) {
      try { router.push('/profile-completion'); } catch {}
    } else {
      try { router.push('/discover'); } catch {}
    }
  } catch (e) {
    let detail = e?.response?.data?.error || e?.message || String(e);
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
