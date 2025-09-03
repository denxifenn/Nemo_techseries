<template>
    <div class="login-container">

    <div class="login-box">
  <h1 class="login-header">Login To Your Account! </h1>

    <div>
    <Form
      :resolver
      @submit="onFormSubmit"
      class="flex flex-col gap-4 w-full sm:w-56"
    >
      <div class="auth-field">
     <FormField
          v-slot="$field"
          as="section"
          name="username"
          initialValue=""
          class="flex flex-col gap-2"
      >
        <InputText type="text" placeholder="Username" class="auth-input-username"/>
         <Message
          v-if="$field?.invalid"
          severity="error"
          size="small"
          variant="simple"
          >{{ $field.error?.message }}</Message
        >
     </FormField>
     <FormField v-slot="$field" asChild name="password" initialValue="">
           <section class="flex flex-col gap-2">
            <Password
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
            >{{ $field.error?.message }}</Message
          >
           </section>
      </FormField>
        </div>
      
      <div class="buttons">
      <Button type="Submit" severity="secondary" label="Submit" class="auth-submit-btn" />
      <Button type="Sign Up" severity="secondary" label="Sign Up" class="auth-signup-btn"/>
      </div>
    </Form>
    </div>

  </div>
</div>
</template>

<script setup>
import { reactive } from "vue";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { z } from "zod";
import { useToast } from "primevue/usetoast";
import { Form, FormField } from "@primevue/forms";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";

const toast = useToast();

const resolver = zodResolver(
  z.object({
    username: z.string().min(1, { message: "Username is required." }),
    password: z.string().min(1, { message: "Password is required." }),
  })
);

const onFormSubmit = ({ valid }) => {
  if (valid) {
    toast.add({
      severity: "success",
      summary: "Form is submitted.",
      life: 3000,
    });
  }
};
</script>

<style scoped>
/* Apply same styling to both input types */

.auth-input-username {
  width: 100%;      /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
  margin-top:5rem;
  margin-left: 0.2rem;
}

.auth-input-password {
  margin-top:3rem;
  width: 100%;      /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
  margin-left: 0.2rem;
}

.auth-submit-btn {
  margin-top:3rem;
  width: 8rem;
  height: 4rem;
  color: rgb(255, 255, 255);
  background: #FFC67B;        /* Orange background */
}

.login-header {
  color:#1c1102; 
  text-align:center;
  font-size: 52px;
  font-family:'Poppins', sans-serif;
  font-size: 2rem;
  margin-top: 1rem;
}

.login-box {
  background-color: orange;
  padding: 5rem;
  border-radius: 8px;
  width: 600px;         /* fixed width */
  display: flex;
  height: 700px;
  flex-direction: column;
  align-items: center;  /* keep header + inputs + button centered inside */
  margin-left: 850px;  
}

.auth-submit-btn{
    color: black; 
    font-family: 'Poppins', 'sans-serif';
    margin-right: 0.5rem;
}

.auth-signup-btn{
    margin-top:1rem;
    width: 8rem;
    height: 4rem;
    color: rgb(255, 255, 255);
    background: #ffa114;        /* Dark background */
    font-family: 'Poppins', 'sans-serif';
}



/* If using a wrapper FormField with flex column, ensure spacing is consistent */
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* consistent space between label and input */
}
</style>
