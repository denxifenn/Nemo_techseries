<template>
  <div id="app">
    <router-view />
    <Toast />
  </div>
</template>

<!-- <script>
export default {
  name: 'App',
}
</script> -->

<script setup>
// import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>