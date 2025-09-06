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
        <a @click="handleLogout" class="nav-link logout-link">
          <i class="pi pi-sign-out"></i>
          <span>Sign Out</span>
        </a>
        <router-link to="/delete-account" class="nav-link delete-link">
          <i class="pi pi-times"></i>
          <span>Delete Account</span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

async function handleLogout() {
  try {
    await authStore.logout();
    router.push('/');
  } catch (error) {
    console.error('Logout failed:', error);
    // Still redirect even if logout fails
    router.push('/');
  }
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: calc(100vh - 80px);
  background: #ec6212;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 116px;
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
  gap: 3rem;
  margin-top: 1rem;
}

.nav-bottom {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 60;
}

.nav-link {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column; /* stack icon above text */
  gap: 0.4rem;
  padding: 0.9rem 1rem;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-link i {
  font-size: 1.6rem; /* bigger icons */
  width: auto;
  line-height: 1;
  text-align: center;
}

.nav-link span {
  display: block;
  font-size: 0.9rem;
}

.logout-link {
  cursor: pointer;
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
    width: 70%;
    min-height: 70%;
    position: sticky;
    padding: 1rem;
    top: 0;
    height: auto;
  }

  .nav-container {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    height: 80px;
  }

  .nav-top {
    flex-direction: row;
    gap: 2rem;
    flex: 1;
    margin-top: 0;
  }

  .nav-bottom {
    flex-direction: row;
    margin-top: 0;
    margin-bottom: 50rem;
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
