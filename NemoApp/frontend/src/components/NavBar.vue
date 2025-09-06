
<template>
    <div class="navbar-container">
        <div class="logo-section">
            <router-link to="/discover" class="logo-link">
                <img src="@/assets/logo.svg" alt="Logo" class="logo-image" />
            </router-link>
        </div>
        <div class="menu-section">
            <Menubar :model="items">
                <template #item="{ item, props, hasSubmenu }">
                    <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
                        <a v-ripple :href="href" v-bind="props.action" @click="navigate">
                            <span :class="item.icon" />
                            <span>{{ item.label }}</span>
                        </a>
                    </router-link>
                    <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
                        <span :class="item.icon" />
                        <span>{{ item.label }}</span>
                        <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
                    </a>
                </template>
            </Menubar>
        </div>
        <div>
            <!-- profile -->
            <router-link to="/profile">
                <button class="profile-button"></button>
            </router-link>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from 'vue-router';
import Menubar from 'primevue/menubar';
import Ripple from 'primevue/ripple';

const router = useRouter();

const items = ref([
    {
        label: 'Create Event',
        icon: 'pi pi-plus',
        route: '/event-creation'
    },
    {
        label: 'Suggest Event',
        icon: 'pi pi-plus',
        route: '/event-suggestion'
    },
    {
        label: 'Friends',
        icon: 'pi pi-users',
        route: '/friends'
    }
]);
</script>

<style scoped>
h4{
    font-size:larger;
    padding-left: 10%;
    font-family: cursive;
    color: #EC7600;
}
.profile-button {
  background-image: url('../assets/profilepic.jpg');
  background-repeat: no-repeat; /* Prevent the image from repeating */
  background-position: center; /* Position the image within the button */
  background-size: cover;
  border: none;
  padding: 42px;
  display: inline-block;
  margin: 8px 8px;
  border-radius: 50%;
  cursor: pointer;
}
/* .navbar-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.5rem 1rem;
} */
.navbar-container {
    position: fixed;     /* Freeze it in place */
    top: 0;              /* Stick to top */
    left: 0;
    right: 0;
    z-index: 1000;       /* Stay above other elements */
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.5rem 1rem;
    background-color: white; /* Add a background so it doesn't overlap text */
    box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* optional subtle shadow */
}

.logo-section {
    flex-shrink: 0;
}

.logo-link {
    display: inline-block;
    text-decoration: none;
}

.logo-image {
    height: 80px;
    width: auto;
    max-width: 150px;
    object-fit: contain;
}

.menu-section {
    flex-grow: 1;
    display: flex;
    justify-content: flex-end;
}

.p-menubar {
    border: none;
    background: transparent;
    width: auto;
}

.p-menubar .p-menuitem {
    margin-left: 1rem;
}



.p-menubar .p-menuitem-link:hover {
    background-color: #ff0000;
}

/* Force menu links and text to black */
::v-deep(.p-menubar .p-menuitem-link),
::v-deep(.p-menubar .p-menuitem-link *){
  color: #000 !important;
}

/* On hover: light grey background, keep black text */
::v-deep(.p-menubar .p-menuitem-link:hover),
::v-deep(.p-menubar .p-menuitem-link:hover *){
  background-color: #f0f0f0 !important;
  color: #000 !important;
}



</style>