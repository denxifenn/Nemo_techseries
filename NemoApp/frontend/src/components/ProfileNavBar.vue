<template>
  <aside class="sidebar">
    <nav class="nav-container">
      <router-link to="/profile" class="nav-link">
        <i class="pi pi-user"></i>
        <span>About Me</span>
      </router-link>
      <router-link to="/friends" class="nav-link">
        <i class="pi pi-users"></i>
        <span>Friends</span>
      </router-link>
      <router-link to="/mybookings" class="nav-link">
        <i class="pi pi-calendar"></i>
        <span>My Bookings</span>
      </router-link>
      <router-link to="/logout" class="nav-link">
        <i class="pi pi-sign-out"></i>
        <span>Sign Out</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
// Simplified navigation component

</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background: #ec6212;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  padding: 1rem 0;
}

.nav-container {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  flex: 1;
  padding: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link i {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

/* Responsive design */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: 100vh;
    position: relative;
    padding: 1rem;
  }

  .nav-container {
    flex: 1;
    padding: 0.5rem;
  }

  .nav-link {
    padding: 0.6rem 0.8rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .sidebar {
    padding: 0.5rem;
  }

  .nav-container {
    padding: 0.25rem;
  }

  .nav-link {
    padding: 0.5rem 0.6rem;
    font-size: 0.8rem;
  }
}
</style>