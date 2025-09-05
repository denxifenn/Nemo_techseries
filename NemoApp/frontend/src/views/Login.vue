<template>
    <div class="login-container">
        <div class="login-box">
            <h1 class="login-header">Login To Your Account!</h1>
            <div>
                <Form
                    :resolver="resolver"
                    @submit="onFormSubmit"
                    class="flex flex-col gap-4 w-full sm:w-56"
                >
                    <!-- PHONE Number -->
                    <div class="auth-field">
                        <FormField
                            v-slot="$field"
                            as="section"
                            name="username"
                            initialValue=""
                            class="flex flex-col gap-2"
                        >
                            <InputText
                                v-model="$field.value"
                                type="text"
                                placeholder="Phone Number"
                                class="auth-input-username"
                            />
                            <Message
                                v-if="$field?.invalid"
                                severity="error"
                                size="small"
                                variant="simple"
                            >
                                {{ $field.error?.message }}
                            </Message>
                        </FormField>

                        <!-- PASSWORD -->
                        <FormField v-slot="$field" asChild name="password" initialValue="">
                            <section class="flex flex-col gap-2">
                                <Password
                                    v-model="$field.value"
                                    type="text"
                                    placeholder="Password"
                                    :feedback="false"
                                    toggleMask
                                    fluid
                                    class="auth-input-password"
                                />
                                <Message
                                    v-if="$field?.invalid"
                                    severity="error"
                                    size="small"
                                    variant="simple"
                                >
                                    {{ $field.error?.message }}
                                </Message>
                            </section>
                        </FormField>
                    </div>

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
                </Form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { z } from "zod";
import { useToast } from "primevue/usetoast";
import { Form, FormField } from "@primevue/forms";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";
import { useRouter } from "vue-router";

const toast = useToast();
const router = useRouter();

const resolver = zodResolver(
    z.object({
        username: z.string().min(1, { message: "Username is required." }),
        password: z.string().min(1, { message: "Password is required." }),
    })
);

const onFormSubmit = (data) => {
    // This will be called when form validation passes
    console.log("Form submitted with data:", data);
};

const handleLogin = () => {
    router.push({ name: "Discover" });
};

const handleSignup = () => {
    router.push({ name: "SignUp" });
};
</script>

<style scoped>
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