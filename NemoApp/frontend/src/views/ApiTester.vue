<template>
  <div class="api-tester">
    <h1>Nemo API Tester</h1>

    <section class="panel config">
      <h2>Configuration</h2>
      <div class="row">
        <label>Backend Base URL</label>
        <input v-model="baseUrlInput" placeholder="http://localhost:5000" />
        <button @click="applyBaseUrl">Apply</button>
        <span class="hint">Current: {{ baseUrl }}</span>
      </div>
      <div class="row">
        <label>Manual Bearer Token</label>
        <input v-model="manualTokenInput" placeholder="Paste JWT here to override Firebase token" />
        <button @click="saveManualToken">Save</button>
        <button @click="clearManualToken">Clear</button>
        <span class="hint">Overrides Firebase token if set</span>
      </div>
      <div class="row">
        <label>Firebase User (Phone)</label>
        <span>{{ currentUserPhone || 'Not signed in' }}</span>
        <button @click="refreshFirebaseToken">Get ID Token</button>
        <button @click="signOutFirebase" :disabled="!currentUserPhone">Sign Out</button>
      </div>
    </section>

    <section class="panel auth">
      <h2>Auth (Firebase + Backend)</h2>
      <div class="row">
        <label>Phone Number (+65)</label>
        <input v-model="authPhone" placeholder="91234567" inputmode="numeric" pattern="[0-9]*" />
        <label>Password</label>
        <input v-model="authPassword" type="password" placeholder="Password123!" />
        <button @click="signupFirebase">Firebase Sign Up</button>
        <button @click="loginFirebase">Firebase Sign In</button>
      </div>
      <div class="row">
        <button @click="backendLogin">Backend Login (provision profile)</button>
        <button @click="backendVerify">Backend Verify Token</button>
      </div>
    </section>

    <section class="panel events">
      <h2>Events</h2>
      <div class="row">
        <label>Filters</label>
        <input v-model="events.filters.category" placeholder="category (sports|workshop|social|cultural)" />
        <input v-model="events.filters.status" placeholder="status (upcoming|completed|cancelled)" />
        <input v-model.number="events.filters.limit" type="number" min="1" max="50" placeholder="limit" />
        <button @click="listEvents">List Events</button>
      </div>
      <div class="row">
        <label>Event ID</label>
        <input v-model="events.eventId" placeholder="event id" />
        <button @click="getEvent">Get Event</button>
      </div>
    </section>

    <section class="panel bookings">
      <h2>Bookings</h2>
      <div class="row">
        <label>Event ID</label>
        <input v-model="bookings.eventId" placeholder="event id" />
        <button @click="createIndividualBooking">Create Individual Booking</button>
      </div>
      <div class="row">
        <label>Group UIDs (ignored; initiator only)</label>
        <input v-model="bookings.groupMembers" placeholder="uid1, uid2" />
        <label>Guest Names (comma-separated)</label>
        <input v-model="bookings.guestNames" placeholder="Alice, Bob" />
        <button @click="createGroupBooking">Create Group Booking</button>
      </div>
      <div class="row">
        <label>Filter</label>
        <select v-model="bookings.filterVal">
          <option value="current">current</option>
          <option value="past">past</option>
          <option value="all">all</option>
        </select>
        <button @click="listMyBookings">List My Bookings</button>
      </div>
      <div class="row">
        <label>Cancel Booking ID</label>
        <input v-model="bookings.cancelId" placeholder="booking_id" />
        <button @click="cancelBooking">Cancel Booking</button>
      </div>
      <div class="row">
        <label>Cancel by Event ID</label>
        <input v-model="bookings.cancelEventId" placeholder="event_id" />
        <button @click="cancelBookingByEvent">Cancel My Booking for Event</button>
      </div>
      <!-- Render current list with per-row cancel buttons -->
      <div v-if="bookingsList.length" class="list">
        <table class="bookings-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>Status</th>
              <th>Event</th>
              <th>Date</th>
              <th>Time</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in bookingsList" :key="b.id">
              <td><code>{{ b.id }}</code></td>
              <td>{{ b.bookingType }}</td>
              <td>{{ b.status }}</td>
              <td>{{ b.event?.title || b.eventId }}</td>
              <td>{{ b.event?.date || '-' }}</td>
              <td>{{ b.event?.time || '-' }}</td>
              <td>
                <button
                  :disabled="(b.status || '').toLowerCase() === 'cancelled'"
                  @click="cancelBooking(b.id)"
                  title="Cancel this booking"
                >
                  Cancel
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="hint">No bookings loaded. Click "List My Bookings", then cancel using the row button.</div>
    </section>

    <section class="panel profile">
      <h2>Profile</h2>
      <div class="row">
        <button @click="getProfile">Get Profile</button>
        <button @click="checkProfileStatus">Check Completion Status</button>
      </div>
      <div class="row">
        <label>Full Name</label>
        <input v-model="profile.fullName" placeholder="Full Name" />
        <label>Age</label>
        <input v-model.number="profile.age" type="number" min="18" max="100" placeholder="Age (18-100)" />
      </div>
      <div class="row">
        <label>Nationality</label>
        <input v-model="profile.nationality" placeholder="e.g., Singaporean" />
        <label>Home Country</label>
        <input v-model="profile.homeCountry" placeholder="e.g., Singapore" />
      </div>
      <div class="row">
        <label>Languages (CSV)</label>
        <input v-model="profile.languagesCsv" placeholder="English, Mandarin" />
        <label>Rest Days (CSV)</label>
        <input v-model="profile.restDaysCsv" placeholder="Saturday, Sunday" />
      </div>
      <div class="row">
        <label>Interests (CSV)</label>
        <input v-model="profile.interestsCsv" placeholder="Football, Cooking" />
        <label>Skills (CSV name:rating)</label>
        <input v-model="profile.skillsCsv" placeholder="Cooking:Proficient, Programming:Expert" />
      </div>
      <div class="row">
        <label>Profile Picture URL</label>
        <input v-model="profile.profilePicture" placeholder="https://..." />
        <button @click="updateProfile">Update Profile</button>
      </div>
      <div class="hint">
        Tips:
        <ul>
          <li>Languages and Interests: comma-separated values.</li>
          <li>Rest Days: weekdays like Monday, Tuesday, ...</li>
          <li>Skills: "name:rating" where rating is Basic | Proficient | Expert.</li>
        </ul>
      </div>
    </section>

    <section class="panel friends">
      <h2>Friends</h2>
      <div class="row">
        <label>Friend Phone Number (+65)</label>
        <input v-model="friends.phoneNumber" placeholder="91234567" inputmode="numeric" pattern="[0-9]*" />
        <button @click="sendFriendRequest">Send Friend Request</button>
      </div>
      <div class="row">
        <label>Request ID</label>
        <input v-model="friends.requestId" placeholder="request_id" />
        <select v-model="friends.action">
          <option value="accept">accept</option>
          <option value="reject">reject</option>
        </select>
        <button @click="handleFriendRequest">Handle Request</button>
      </div>
      <div class="row">
        <button @click="listFriends">List Friends</button>
      </div>
    </section>

    <section class="panel suggestions">
      <h2>Suggestions</h2>
      <div class="row">
        <label>Text</label>
        <input v-model="suggestions.text" placeholder="Your suggestion..." />
        <button @click="createSuggestion">Submit Suggestion</button>
      </div>
      <div class="row">
        <button @click="listSuggestions">List Suggestions (Admin)</button>
      </div>
    </section>

    <section class="panel admin">
      <h2>Admin</h2>
      <div class="row">
        <button @click="adminHealth">Admin Health</button>
      </div>
      <div class="row grid">
        <input v-model="adminForm.title" placeholder="Title" />
        <input v-model="adminForm.description" placeholder="Description" />
        <input v-model="adminForm.category" placeholder="Category (sports|workshop|social|cultural)" />
        <input v-model="adminForm.location" placeholder="Location" />
        <input v-model="adminForm.date" placeholder="YYYY-MM-DD" />
        <input v-model="adminForm.time" placeholder="HH:MM (24h)" />
        <input v-model.number="adminForm.maxParticipants" type="number" min="1" placeholder="Max Participants" />
        <input v-model="adminForm.imageUrl" placeholder="Image URL (optional)" />
        <button @click="adminCreateEvent">Create Event</button>
      </div>

      <h3>Update Event</h3>
      <div class="row">
        <label>Event ID</label>
        <input v-model="adminUpdate.eventId" placeholder="event_id to update" />
      </div>
      <div class="row grid">
        <input v-model="adminUpdate.title" placeholder="Title (optional)" />
        <input v-model="adminUpdate.description" placeholder="Description (optional)" />
        <input v-model="adminUpdate.category" placeholder="Category (sports|workshop|social|cultural)" />
        <input v-model="adminUpdate.location" placeholder="Location (optional)" />
        <input v-model="adminUpdate.date" placeholder="YYYY-MM-DD (optional)" />
        <input v-model="adminUpdate.time" placeholder="HH:MM (24h, optional)" />
        <input v-model.number="adminUpdate.maxParticipants" type="number" min="1" placeholder="Max Participants (optional)" />
        <input v-model="adminUpdate.imageUrl" placeholder="Image URL (optional)" />
        <button @click="adminUpdateEvent">Update Event</button>
      </div>
    </section>

    <section class="panel result">
      <h2>Result</h2>
      <div v-if="lastError" class="error">{{ lastError }}</div>
      <pre class="json">{{ pretty(lastResponse) }}</pre>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import api from '../services/api';
import {
  auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  getIdToken,
  onAuth
} from '../services/firebase';
import { formatSingaporePhone, phoneToEmail, emailToPhone } from '../utils/phoneUtils';

const toast = useToast();

// Config state
const baseUrl = ref(api.getBaseUrl());
const baseUrlInput = ref(baseUrl.value);

const manualTokenInput = ref(api.getManualToken());

// Auth state
const authPhone = ref('');
const authPassword = ref('');
const currentUserPhone = ref('');

// Subscriptions
onMounted(() => {
  baseUrl.value = api.getBaseUrl();
  baseUrlInput.value = baseUrl.value;
  manualTokenInput.value = api.getManualToken();
  // Track current user
  onAuth((user) => {
    const alias = user?.email || '';
    currentUserPhone.value = emailToPhone(alias) || '';
  });
});

// Helpers
function pretty(obj) {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

const lastResponse = ref(null);
const lastError = ref('');
const bookingsList = ref([]);

// UI actions - config
function applyBaseUrl() {
  api.setBaseUrl(baseUrlInput.value || '');
  baseUrl.value = api.getBaseUrl();
  toast.add({ severity: 'success', summary: 'Base URL updated', detail: baseUrl.value, life: 2500 });
}

function saveManualToken() {
  api.setManualToken(manualTokenInput.value || '');
  toast.add({ severity: 'success', summary: 'Manual token saved', life: 2000 });
}

function clearManualToken() {
  api.clearManualToken();
  manualTokenInput.value = '';
  toast.add({ severity: 'success', summary: 'Manual token cleared', life: 2000 });
}

// UI actions - auth
async function signupFirebase() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const formatted = formatSingaporePhone(authPhone.value);
    const alias = phoneToEmail(formatted);
    const cred = await createUserWithEmailAndPassword(auth, alias, authPassword.value);
    lastResponse.value = { success: true, user: { uid: cred.user.uid, phoneNumber: formatted } };
    toast.add({ severity: 'success', summary: 'Firebase Sign Up', detail: formatted, life: 3000 });
  } catch (e) {
    const msg = e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Firebase Sign Up failed', detail: msg, life: 4000 });
  }
}

async function loginFirebase() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const formatted = formatSingaporePhone(authPhone.value);
    const alias = phoneToEmail(formatted);
    const cred = await signInWithEmailAndPassword(auth, alias, authPassword.value);
    lastResponse.value = { success: true, user: { uid: cred.user.uid, phoneNumber: formatted } };
    toast.add({ severity: 'success', summary: 'Firebase Sign In', detail: formatted, life: 3000 });
  } catch (e) {
    const msg = e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Firebase Sign In failed', detail: msg, life: 4000 });
  }
}

async function signOutFirebase() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    await signOut();
    currentUserPhone.value = '';
    lastResponse.value = { success: true, message: 'Signed out' };
    toast.add({ severity: 'success', summary: 'Signed out', life: 2500 });
  } catch (e) {
    const msg = e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Sign out failed', detail: msg, life: 4000 });
  }
}

async function refreshFirebaseToken() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const token = await getIdToken(true);
    const preview = token ? token.substring(0, 25) + '...' : null;
    lastResponse.value = { success: !!token, tokenPreview: preview };
    if (token) {
      toast.add({ severity: 'success', summary: 'ID Token Fetched', detail: preview, life: 3000 });
    } else {
      toast.add({ severity: 'warn', summary: 'No token', detail: 'Not signed in', life: 3000 });
    }
  } catch (e) {
    const msg = e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Get ID Token failed', detail: msg, life: 4000 });
  }
}

async function backendLogin() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const token = await getIdToken(true);
    if (!token) throw new Error('No Firebase token. Sign in first or set manual token and use backendVerify instead.');
    // Pass phoneNumber to provision profile
    const resp = await api.backendLoginWithIdToken(token, {
      phoneNumber: currentUserPhone.value || undefined,
    });
    lastResponse.value = resp.data || resp;
    const label = resp?.data?.user?.phoneNumber || resp?.data?.user?.uid || 'unknown';
    toast.add({ severity: 'success', summary: 'Backend Login', detail: `Provisioned ${label}`, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Backend Login failed', detail: msg, life: 4000 });
  }
}

async function backendVerify() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const resp = await api.backendVerify();
    lastResponse.value = resp.data || resp;
    toast.add({ severity: 'success', summary: 'Backend Verify', detail: 'Token is valid', life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Backend Verify failed', detail: msg, life: 4000 });
  }
}

// Events
const events = reactive({
  filters: { category: '', status: '', limit: 20 },
  eventId: '',
});

async function listEvents() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const { category, status, limit } = events.filters;
    const resp = await api.get('/api/events', {
      category: category || undefined,
      status: status || undefined,
      limit: limit || undefined,
    });
    lastResponse.value = resp.data || resp;
    const count = (resp?.data?.count ?? resp?.data?.events?.length) ?? 0;
    toast.add({ severity: 'success', summary: 'Events fetched', detail: `Count: ${count}`, life: 2500 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'List Events failed', detail: msg, life: 4000 });
  }
}

async function getEvent() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!events.eventId) throw new Error('eventId required');
    const resp = await api.get(`/api/events/${events.eventId}`);
    lastResponse.value = resp.data || resp;
    toast.add({ severity: 'success', summary: 'Event fetched', detail: events.eventId, life: 2500 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Get Event failed', detail: msg, life: 4000 });
  }
}

// Bookings
const bookings = reactive({
  eventId: '',
  groupMembers: '',
  guestNames: '',
  filterVal: 'current',
  cancelId: '',
  cancelEventId: '',
});

async function createIndividualBooking() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!bookings.eventId) throw new Error('eventId required');
    const resp = await api.post('/api/bookings/individual', { eventId: bookings.eventId });
    lastResponse.value = resp.data || resp;
    const id = resp?.data?.bookingId || 'unknown';
    toast.add({ severity: 'success', summary: 'Individual booking created', detail: id, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Create Individual Booking failed', detail: msg, life: 4000 });
  }
}

function parseCsv(input) {
  if (!input) return [];
  return input
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0);
}

// Parse "Name:Rating" pairs separated by commas into [{name, rating}]
function parseSkills(input) {
  if (!input) return [];
  const out = [];
  for (const item of input.split(',')) {
    const pair = String(item || '').trim();
    if (!pair) continue;
    const [nameRaw, ratingRaw] = pair.split(':').map(t => String(t || '').trim());
    if (!nameRaw) continue;
    const ratingLc = String(ratingRaw || 'Basic').trim().toLowerCase();
    let rating = 'Basic';
    if (ratingLc === 'proficient') rating = 'Proficient';
    else if (ratingLc === 'expert') rating = 'Expert';
    else rating = 'Basic';
    out.push({ name: nameRaw, rating });
  }
  return out;
}

async function createGroupBooking() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!bookings.eventId) throw new Error('eventId required');
    const groupMembers = parseCsv(bookings.groupMembers);
    const groupMemberNames = parseCsv(bookings.guestNames);
    const resp = await api.post('/api/bookings/group', {
      eventId: bookings.eventId,
      groupMembers,      // backend ignores UIDs (initiator only), but we pass through for transparency
      groupMemberNames,
    });
    lastResponse.value = resp.data || resp;
    const count = resp?.data?.joinedCount ?? 'n/a';
    toast.add({ severity: 'success', summary: 'Group booking created', detail: `Joined: ${count}`, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Create Group Booking failed', detail: msg, life: 4000 });
  }
}

async function listMyBookings() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const resp = await api.get('/api/bookings/my', { filter: bookings.filterVal || 'current' });
    lastResponse.value = resp.data || resp;
    bookingsList.value = resp?.data?.bookings || [];
    const count = (resp?.data?.count ?? bookingsList.value.length) ?? 0;
    toast.add({ severity: 'success', summary: 'My bookings', detail: `Count: ${count}`, life: 2500 });
  } catch (e) {
    bookingsList.value = [];
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'List My Bookings failed', detail: msg, life: 4000 });
  }
}

async function cancelBooking(id) {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const bookingId = id || bookings.cancelId;
    if (!bookingId) throw new Error('bookingId required');
    const resp = await api.del(`/api/bookings/${bookingId}`);
    lastResponse.value = resp.data || resp;
    const freed = resp?.data?.seatsFreed ?? 0;
    toast.add({ severity: 'success', summary: 'Booking cancelled', detail: `Seats freed: ${freed}`, life: 3000 });
    // Refresh list after cancellation
    try { await listMyBookings(); } catch {}
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Cancel Booking failed', detail: msg, life: 4000 });
  }
}

async function cancelBookingByEvent() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!bookings.cancelEventId) throw new Error('eventId required');
    const resp = await api.del(`/api/bookings/by-event/${bookings.cancelEventId}`);
    lastResponse.value = resp.data || resp;
    const freed = resp?.data?.seatsFreed ?? 0;
    toast.add({ severity: 'success', summary: 'Booking cancelled (by event)', detail: `Seats freed: ${freed}`, life: 3000 });
    // Refresh list after cancellation
    try { await listMyBookings(); } catch {}
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Cancel by Event failed', detail: msg, life: 4000 });
  }
}

// Profile
const profile = reactive({
  fullName: '',
  age: null,
  nationality: '',
  languagesCsv: '',
  homeCountry: '',
  restDaysCsv: '',
  interestsCsv: '',
  skillsCsv: '',
  profilePicture: '',
});

async function getProfile() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const resp = await api.get('/api/profile');
    lastResponse.value = resp.data || resp;
    const uid = resp?.data?.profile?.uid || 'unknown';
    toast.add({ severity: 'success', summary: 'Profile fetched', detail: uid, life: 2500 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Get Profile failed', detail: msg, life: 4000 });
  }
}

async function updateProfile() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const body = {};
    if (profile.fullName) body.fullName = profile.fullName;
    if (profile.age != null && profile.age !== '') body.age = Number(profile.age);
    if (profile.nationality) body.nationality = profile.nationality;
    if (profile.languagesCsv) body.languages = parseCsv(profile.languagesCsv);
    if (profile.homeCountry) body.homeCountry = profile.homeCountry;
    if (profile.restDaysCsv) body.restDays = parseCsv(profile.restDaysCsv);
    if (profile.interestsCsv) body.interests = parseCsv(profile.interestsCsv);
    if (profile.skillsCsv) body.skills = parseSkills(profile.skillsCsv);
    if (profile.profilePicture) body.profilePicture = profile.profilePicture;

    if (Object.keys(body).length === 0) {
      throw new Error('No fields to update');
    }

    const resp = await api.put('/api/profile', body);
    lastResponse.value = resp.data || resp;

    const fields = Object.keys(body).join(', ');
    const completed = resp?.data?.profileCompleted;
    const missing = (resp?.data?.missingFields || []).join(', ');
    const detail = completed ? `Updated: ${fields}. Profile completed.` : `Updated: ${fields}. Missing: ${missing}`;
    toast.add({ severity: 'success', summary: 'Profile updated', detail, life: 4000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Update Profile failed', detail: msg, life: 4000 });
  }
}

// Friends
const friends = reactive({
  phoneNumber: '',
  requestId: '',
  action: 'accept',
});

async function sendFriendRequest() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!friends.phoneNumber) throw new Error('phoneNumber required');
    const resp = await api.post('/api/friends/request', { phoneNumber: friends.phoneNumber });
    lastResponse.value = resp.data || resp;
    const id = resp?.data?.requestId || 'unknown';
    toast.add({ severity: 'success', summary: 'Friend request sent', detail: id, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Send Friend Request failed', detail: msg, life: 4000 });
  }
}

async function handleFriendRequest() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!friends.requestId) throw new Error('requestId required');
    if (!['accept', 'reject'].includes(friends.action)) throw new Error('action must be accept or reject');
    const resp = await api.put(`/api/friends/request/${friends.requestId}`, { action: friends.action });
    lastResponse.value = resp.data || resp;
    toast.add({ severity: 'success', summary: 'Friend request handled', detail: friends.action, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Handle Friend Request failed', detail: msg, life: 4000 });
  }
}

async function listFriends() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const resp = await api.get('/api/friends');
    lastResponse.value = resp.data || resp;
    const count = resp?.data?.count ?? (resp?.data?.friends?.length ?? 0);
    toast.add({ severity: 'success', summary: 'Friends fetched', detail: `Count: ${count}`, life: 2500 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'List Friends failed', detail: msg, life: 4000 });
  }
}

// Suggestions
const suggestions = reactive({
  text: '',
});

async function createSuggestion() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!suggestions.text) throw new Error('text required');
    const resp = await api.post('/api/suggestions', { text: suggestions.text });
    lastResponse.value = resp.data || resp;
    const id = resp?.data?.suggestionId || 'unknown';
    toast.add({ severity: 'success', summary: 'Suggestion submitted', detail: id, life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Submit Suggestion failed', detail: msg, life: 4000 });
  }
}

async function listSuggestions() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const resp = await api.get('/api/suggestions');
    lastResponse.value = resp.data || resp;
    const count = resp?.data?.count ?? (resp?.data?.suggestions?.length ?? 0);
    toast.add({ severity: 'success', summary: 'Suggestions fetched', detail: `Count: ${count}`, life: 2500 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'List Suggestions failed', detail: msg, life: 4000 });
  }
}

// Admin
const adminForm = reactive({
  title: '',
  description: '',
  category: '',
  location: '',
  date: '',
  time: '',
  maxParticipants: 10,
  imageUrl: '',
});

async function adminHealth() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    const resp = await api.get('/api/admin/health');
    lastResponse.value = resp.data || resp;
    const msg = resp?.data?.message || 'OK';
    toast.add({ severity: 'success', summary: 'Admin Health', detail: msg, life: 2500 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Admin Health failed', detail: msg, life: 4000 });
  }
}

const adminUpdate = reactive({
  eventId: '',
  title: '',
  description: '',
  category: '',
  location: '',
  date: '',
  time: '',
  maxParticipants: null,
  imageUrl: '',
});

async function adminUpdateEvent() {
  lastError.value = '';
  lastResponse.value = null;
  try {
    if (!adminUpdate.eventId) throw new Error('eventId required');
    const body = {};
    if (adminUpdate.title) body.title = adminUpdate.title;
    if (adminUpdate.description) body.description = adminUpdate.description;
    if (adminUpdate.category) body.category = adminUpdate.category;
    if (adminUpdate.location) body.location = adminUpdate.location;
    if (adminUpdate.date) body.date = adminUpdate.date;
    if (adminUpdate.time) body.time = adminUpdate.time;
    if (adminUpdate.imageUrl) body.imageUrl = adminUpdate.imageUrl;
    if (adminUpdate.maxParticipants != null && adminUpdate.maxParticipants !== '') {
      body.maxParticipants = Number(adminUpdate.maxParticipants);
    }
    const resp = await api.put(`/api/admin/events/${adminUpdate.eventId}`, body);
    lastResponse.value = resp.data || resp;
    toast.add({ severity: 'success', summary: 'Event updated', life: 3000 });
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    lastError.value = msg;
    toast.add({ severity: 'error', summary: 'Update Event failed', detail: msg, life: 4000 });
  }
}
</script>

<style scoped>
.api-tester {
  max-width: 1000px;
  margin: 20px auto 80px auto;
  padding: 0 16px 24px 16px;
  text-align: left;
}

.panel {
  border: 1px solid #ddd;
  padding: 12px;
  margin-bottom: 16px;
  border-radius: 8px;
  background: #fafafa;
}

.panel h2 {
  margin-top: 0;
  font-size: 18px;
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin: 6px 0;
}

.row input, .row select {
  padding: 6px 8px;
  min-width: 220px;
}

.row button {
  padding: 6px 12px;
}

.row .hint {
  font-size: 12px;
  color: #666;
}

.grid {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.result .json {
  background: #111;
  color: #0f0;
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
  max-height: 400px;
  font-size: 12px;
}

.error {
  color: #b00020;
  margin-bottom: 8px;
  font-weight: bold;
}
</style>