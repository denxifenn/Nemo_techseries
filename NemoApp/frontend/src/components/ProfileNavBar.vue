<template>
  <aside class="sidebar">
    <nav class="nav-container">
      <div class="nav-top">
        <router-link to="/profile" class="nav-link">
          <i class="pi pi-user"></i>
          <span>About Me</span>
        </router-link>
        <router-link to="/friends" class="nav-link">
          <i class="pi pi-users"></i>
          <span>Friends</span>
        </router-link>
        <router-link to="/my-bookings" class="nav-link">
          <i class="pi pi-calendar"></i>
          <span>My Bookings</span>
        </router-link>
      </div>
      
      <div class="nav-bottom">
        <router-link to="/logout" class="nav-link logout-link">
          <i class="pi pi-sign-out"></i>
          <span>Sign Out</span>
        </router-link>
        <router-link to="/delete-account" class="nav-link delete-link">
          <i class="pi pi-times"></i>
          <span>Delete Account</span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup>
// Simplified navigation component
</script>

<style scoped>
.sidebar {
  width: 250px;
  min-height: 100vh;
  background: #ec6212;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  padding: 1rem 0;
}

.nav-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
  padding: 1rem;
}

.nav-top {
  display: flex;
  flex-direction: column;
  gap: 6rem;
  margin-top: 9rem;
}

.nav-bottom {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
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

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-link i {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.logout-link:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.delete-link {
  background-color: rgba(220, 38, 38, 0.2);
  border: 1px solid rgba(220, 38, 38, 0.3);
}

.delete-link:hover {
  background-color: rgba(220, 38, 38, 0.3);
}

/* Responsive design */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    min-height: auto;
    position: relative;
    padding: 1rem;
  }

  .nav-container {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    height: auto;
  }

  .nav-top {
    flex-direction: row;
    gap: 0.25rem;
    flex: 1;
  }

  .nav-bottom {
    flex-direction: row;
    gap: 0.25rem;
    margin-top: 0;
  }

  .nav-link {
    padding: 0.6rem 0.8rem;
    font-size: 0.85rem;
    flex-direction: column;
    gap: 0.25rem;
    text-align: center;
    flex: 1;
  }

  .nav-link span {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .nav-link {
    padding: 0.5rem 0.3rem;
    font-size: 0.8rem;
  }
  
  .nav-link span {
    font-size: 0.7rem;
  }
}
</style>