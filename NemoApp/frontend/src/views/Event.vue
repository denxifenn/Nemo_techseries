<template>
  <div>
    <h1>{{ componentName }}</h1>
    <!-- <NavBar/> -->
  </div>
</template>

<script>
// import NavBar from '../components/NavBar.vue'; // Adjust path as needed

export default {
  name: 'Event',
  // components: {
  //       NavBar // Register the component for local use
  //     },
  data() {
    return {
      componentName: 'Event'
    }
  }
}
</script>

<style>
</style>
