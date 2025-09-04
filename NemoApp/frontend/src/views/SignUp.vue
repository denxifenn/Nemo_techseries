<template>
  <div class="signup-container">
    <div class="signup-box">
      <h1 class="signup-header">SIGN UP FOR AN ACCOUNT!</h1>
      <div class="card flex justify-center">
        <Form
          :initialValues
          :resolver
          @submit="onFormSubmit"
          class="flex flex-col gap-4 w-full sm:w-80"
        >
          <!-- <FormField v-slot="$field" name="username" initialValue="" :resolver="zodUserNameResolver" class="flex flex-col gap-1">
                <InputText type="text" placeholder="Username" />
                <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{ $field.error?.message }}</Message>
            </FormField>  -->
          <FormField
            v-slot="$field"
            name="firstname"
            initialValue=""
            :resolver="yupFirstNameResolver"
            class="flex flex-col gap-1"
          >
            <InputText
              type="text"
              placeholder="First Name"
              class="first-name-btn"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
              >{{ $field.error?.message }}</Message
            >
          </FormField>

          <FormField
            v-slot="$field"
            name="lastname"
            initialValue=""
            :resolver="valibotLastNameResolver"
            class="flex flex-col gap-1"
          >
            <InputText
              type="text"
              placeholder="Last Name"
              class="last-name-btn"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
              >{{ $field.error?.message }}</Message
            >
          </FormField>

          <FormField
            v-slot="$field"
            name="Phone Number"
            initialValue=""
            :resolver="phoneNumberResolver"
            class="flex flex-col gap-1"
          >
            <InputNumber
              type="text"
              placeholder="Phone Number"
              class="phone-number-btn"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
              >{{ $field.error?.message }}</Message
            >
          </FormField>

          <FormField
            v-slot="$field"
            name="FIN Number"
            initialValue=""
            :resolver="finNumberResolver"
            class="flex flex-col gap-1"
          >
            <InputText
              type="text"
              placeholder="FIN Number"
              class="FIN-number-btn"
              maxlength="9"
              v-bind="$field"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
              >{{ $field.error?.message }}</Message
            >
          </FormField>

          <FormField
            v-slot="$field"
            name="password"
            initialValue=""
            :resolver="customPasswordResolver"
            class="flex flex-col gap-1"
          >
            <Password
              type="text"
              placeholder="Password"
              :feedback="false"
              toggleMask
              fluid
              class="password-btn"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
              >{{ $field.error?.message }}</Message
            >
          </FormField>
          <Button
            type="I"
            severity="secondary"
            label="Sign Up"
            style="background-color: #ffa690; color: black; font-weight: bold;"
            class="submit-btn"
          />
        </Form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { valibotResolver } from "@primevue/forms/resolvers/valibot";
import { yupResolver } from "@primevue/forms/resolvers/yup";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import * as v from "valibot";
import * as yup from "yup";
import { z } from "zod";
import { useToast } from "primevue/usetoast";

// Import PrimeVue form components
import { Form, FormField } from "@primevue/forms";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";

const toast = useToast();

const initialValues = reactive({
  details: "",
});

const resolver = zodResolver(
  z.object({
    details: z
      .string()
      .min(1, { message: "Details is required via Form Resolver." }),
  })
);

const zodUserNameResolver = zodResolver(
  z.string().min(1, { message: "Username is required." })
);
const yupFirstNameResolver = yupResolver(
  yup.string().required("First name is required.")
);
const valibotLastNameResolver = valibotResolver(
  v.pipe(v.string(), v.minLength(1, "Last name is required."))
);

const phoneNumberResolver = valibotResolver(
  v.pipe(
    v.number("Phone Number must be numeric."), // Custom error message
    v.minValue(10000000, "Phone Number is too short."), // Example: 8 digits
    v.maxValue(99999999, "Phone Number is too long.")   // Example: 8 digits
  )
);

const finNumberResolver = valibotResolver(
  v.pipe(
    v.string("FIN Number is required."),
    v.minLength(9, "FIN Number must be 9 characters."),
    v.maxLength(9, "FIN Number must be 9 characters."),
    v.regex(/^[A-Za-z][0-9]{8}$/, "FIN Number must start with a letter followed by 8 digits.")
  )
);

const customPasswordResolver = ({ value }) => {
  const errors = [];

  if (!value) {
    errors.push({ message: "Password is required via Custom." });
  }

  return {
    errors,
  };
};

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

.signup-container {
  background-image: url("@/assets/workers_background.jpg"); /* use a high-res image */
  background-size: cover; /* cover whole container */
  background-position: center; /* center image */
  background-repeat: no-repeat;
  min-height: 100vh; /* full viewport height */
  width: 100%;
  display: flex;
  justify-content: center; /* center login box horizontally */
  align-items: center; /* center login box vertically */
}

.signup-box {
  background-color: #ffa600;
  padding: 5rem;
  border-radius: 8px;
  width: 700px; /* fixed width */
  display: flex;
  height: 800px;
  flex-direction: column;
  align-items: center; /* keep header + inputs + button centered inside */
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
  width: 100%; /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.last-name-btn {
  width: 100%; /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.phone-number-btn {
  width: 100%; /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.FIN-number-btn {
  width: 100%; /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
  margin-top: 3rem;
  margin-left: 0.2rem;
}

.password-btn {
  width: 100%; /* make them full width of parent container */
  min-height: 2.5rem; /* set a consistent height */
  font-size: 1rem;
  box-sizing: border-box; /* include padding in height */
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
</style>
