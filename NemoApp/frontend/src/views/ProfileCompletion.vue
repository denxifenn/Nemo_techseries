<template>
  <div class="profile-completion-page">
    <div class="card">
      <h1 class="title">Complete Your Profile</h1>
      <p class="subtitle">
        Please complete your profile to continue. You can edit this information later in your Profile page.
      </p>

      <form @submit.prevent="submitProfile" class="form">
        <div class="form-row">
          <label>Full Name *</label>
          <InputText v-model="form.fullName" placeholder="Enter your full name" />
        </div>

        <div class="form-row two-col">
          <div class="col">
            <label>Age *</label>
            <InputNumber v-model="form.age" :min="18" :max="100" placeholder="Age" />
          </div>
          <div class="col">
            <label>Nationality *</label>
            <InputText v-model="form.nationality" placeholder="e.g., Singaporean" />
          </div>
        </div>

        <div class="form-row">
          <label>Languages *</label>
          <Chips v-model="form.languages" separator="," placeholder="e.g., English, Mandarin" />
          <small class="hint">Press Enter after each language</small>
        </div>

        <div class="form-row two-col">
          <div class="col">
            <label>Home Country *</label>
            <InputText v-model="form.homeCountry" placeholder="e.g., Singapore" />
          </div>
          <div class="col">
            <label>Rest Days *</label>
            <MultiSelect
              v-model="form.restDays"
              :options="weekdayOptions"
              optionLabel="label"
              optionValue="value"
              display="chip"
              placeholder="Select your rest days"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-row">
          <label>Interests (optional)</label>
          <Chips v-model="form.interests" separator="," placeholder="e.g., Football, Cooking" />
        </div>

        <div class="form-row">
          <label>Skills (optional)</label>
          <div class="skills">
            <div
              class="skill-row"
              v-for="(s, idx) in form.skills"
              :key="idx"
            >
              <InputText v-model="s.name" placeholder="Skill name" class="skill-name" />
              <Select
                v-model="s.rating"
                :options="skillRatings"
                optionLabel="label"
                optionValue="value"
                placeholder="Rating"
                class="skill-rating"
              />
              <Button icon="pi pi-trash" severity="danger" text @click="removeSkill(idx)" />
            </div>
            <Button icon="pi pi-plus" label="Add Skill" text @click="addSkill" />
          </div>
        </div>

        <div class="actions">
          <Button
            type="submit"
            label="Save and Continue"
            class="submit-btn"
            :loading="saving"
          />
        </div>

        <Message v-if="error" severity="error" class="mt-2">{{ error }}</Message>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Select from 'primevue/select';
import MultiSelect from 'primevue/multiselect';
import Chips from 'primevue/chips';
import Button from 'primevue/button';
import Message from 'primevue/message';

import { useAuthStore } from '../stores/auth';

const router = useRouter();
const route = useRoute();
const toast = useToast();
const auth = useAuthStore();

const saving = ref(false);
const error = ref('');

const weekdayOptions = [
  { label: 'Monday', value: 'Monday' },
  { label: 'Tuesday', value: 'Tuesday' },
  { label: 'Wednesday', value: 'Wednesday' },
  { label: 'Thursday', value: 'Thursday' },
  { label: 'Friday', value: 'Friday' },
  { label: 'Saturday', value: 'Saturday' },
  { label: 'Sunday', value: 'Sunday' },
];

const skillRatings = [
  { label: 'Basic', value: 'Basic' },
  { label: 'Proficient', value: 'Proficient' },
  { label: 'Expert', value: 'Expert' },
];

const form = ref({
  fullName: '',
  age: null,
  nationality: '',
  languages: [],
  homeCountry: '',
  restDays: [],
  interests: [],
  skills: []
});

function addSkill() {
  form.value.skills.push({ name: '', rating: 'Basic' });
}
function removeSkill(idx) {
  form.value.skills.splice(idx, 1);
}

async function loadProfile() {
  // Prefill form with any existing values
  const res = await auth.fetchProfile();
  if (res?.success && res.profile) {
    const p = res.profile;
    form.value.fullName = p.fullName || '';
    form.value.age = p.age ?? null;
    form.value.nationality = p.nationality || '';
    form.value.languages = Array.isArray(p.languages) ? p.languages : [];
    form.value.homeCountry = p.homeCountry || '';
    form.value.restDays = Array.isArray(p.restDays) ? p.restDays : [];
    form.value.interests = Array.isArray(p.interests) ? p.interests : [];
    form.value.skills = Array.isArray(p.skills) ? p.skills : [];
  }
}

async function submitProfile() {
  error.value = '';
  saving.value = true;
  try {
    // Basic validation aligned with backend
    if (!form.value.fullName?.trim()) throw new Error('Full name is required');
    if (!Number.isInteger(form.value.age) || form.value.age < 18 || form.value.age > 100) {
      throw new Error('Age must be an integer between 18 and 100');
    }
    if (!form.value.nationality?.trim()) throw new Error('Nationality is required');
    if (!Array.isArray(form.value.languages) || form.value.languages.length === 0) {
      throw new Error('At least one language is required');
    }
    if (!form.value.homeCountry?.trim()) throw new Error('Home country is required');
    if (!Array.isArray(form.value.restDays) || form.value.restDays.length === 0) {
      throw new Error('Select at least one rest day');
    }

    const payload = {
      fullName: form.value.fullName.trim(),
      age: form.value.age,
      nationality: form.value.nationality.trim(),
      languages: form.value.languages.map(l => String(l).trim()).filter(Boolean),
      homeCountry: form.value.homeCountry.trim(),
      restDays: form.value.restDays.slice(),
      interests: (form.value.interests || []).map(i => String(i).trim()).filter(Boolean),
      skills: (form.value.skills || []).filter(s => s?.name && s?.rating).map(s => ({
        name: String(s.name).trim().slice(0, 50),
        rating: String(s.rating).trim()
      }))
    };

    const res = await auth.updateProfile(payload);
    if (res?.success) {
      toast.add({ severity: 'success', summary: 'Profile saved', life: 2500 });
      const redirect = route.query.redirect || '/discover';
      router.replace(String(redirect));
    } else {
      throw new Error(res?.error || 'Failed to update profile');
    }
  } catch (e) {
    error.value = e?.message || String(e);
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  // Ensure auth state
  if (!auth.isAuthenticated) {
    await auth.initializeAuth();
  }
  // Load current values if any
  await loadProfile();
});
</script>

<style scoped>
.profile-completion-page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
  background: #f9fafb;
}

.card {
  background: white;
  width: 100%;
  max-width: 850px;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  color: #111827;
}

.subtitle {
  color: #6b7280;
  margin: 0.25rem 0 1.5rem 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.col {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hint {
  color: #9ca3af;
}

.skills {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skill-row {
  display: grid;
  grid-template-columns: 1fr 220px auto;
  gap: 0.5rem;
  align-items: center;
}

.skill-name {
  width: 100%;
}

.skill-rating {
  width: 100%;
}

.actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  background: #EC7600;
  border: none;
}
</style>