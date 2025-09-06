<template>
  <div id="app">
    <NavBar/>
    <router-view />
    <Toast />
  </div>
</template>

<script setup>
import Toast from 'primevue/toast';
import NavBar from './components/NavBar.vue';
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
</style>