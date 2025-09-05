<template>
  <aside class="sidebar">
    <!-- Top Links -->
    <nav class="nav-top">
      <router-link to="/profile" class="nav-btn">
        <Button icon="pi pi-user" label="About Me" class="nav-btn" text />
      </router-link>
      <router-link to="/friends" class="nav-btn">
        <Button icon="pi pi-users" label="Friends" class="nav-btn" text />
      </router-link>
      <router-link to="/mybookings" class="nav-btn">
        <Button icon="pi pi-calendar" label="My Bookings" class="nav-btn" text />
      </router-link>
    </nav>

    <!-- Bottom Links -->
    <div class="nav-bottom">
      <router-link to="/logout" class="nav-btn">
        <Button icon="pi pi-sign-out" label="Sign Out" class="nav-btn" text />
      </router-link>
      <router-link to="/delete-account" class="nav-btn">
        <Button icon="pi pi-trash" label="Delete Account" class="nav-btn" severity="danger" text/>
      </router-link>
    </div>
  </aside>
</template>

<script setup>
import Button from 'primevue/button';

</script>

<style scoped>
.sidebar {
  /* position:fixed; */
  width: 250px;
  height: 90vh;
  left: 0;
  top: 5;
  background-color: #ec6212;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: sticky;

}

.nav-top {
  margin-top: 12rem;
  display: flex;
  flex-direction: column;
  gap: 6rem;
}

.nav-bottom {
  display: flex;
  flex-direction: column;
  margin-top: auto;
  gap:2.5rem;
  margin-bottom: 6rem;
}

.nav-btn .p-button {
  justify-content: flex-start; /* icon + text aligned left */
  color: white;
}
/* 
.nav-btn .p-button:hover {
  background-color: #e35513; 
} */
</style>