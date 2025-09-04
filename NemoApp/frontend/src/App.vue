<template>
  <div id="app">
    <nav class="topnav">
      <router-link to="/api-tester">API Tester</router-link>
      <span class="spacer"></span>
      <router-link to="/login">Login</router-link>
      <router-link to="/signup">Sign Up</router-link>
      <router-link to="/discover">Discover</router-link>
    </nav>
    <router-view />
    <Toast />
  </div>
</template>

<script setup>
import Toast from 'primevue/toast';
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
  margin-top: 60px;
}

.topnav {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  background: #f6f6f6;
  border-bottom: 1px solid #ddd;
}

.topnav a {
  text-decoration: none;
  color: #1976d2;
  font-weight: 600;
}

.topnav .spacer {
  flex: 1;
}
</style>