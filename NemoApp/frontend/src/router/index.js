import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import SignUp from '../views/SignUp.vue'
import Discover from '../views/Discover.vue'
import Event from '../views/Event.vue'
import EventCreation from '../views/EventCreation.vue'
import EventSuggestion from '../views/EventSuggestion.vue'
import Profile from '../views/Profile.vue'
import Friends from '../views/Friends.vue'
import FriendInfo from '../views/FriendInfo.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp
  },
  {
    path: '/discover',
    name: 'Discover',
    component: Discover
  },
  {
    path: '/event',
    name: 'Event',
    component: Event
  },
  {
    path: '/event-creation',
    name: 'EventCreation',
    component: EventCreation
  },
  {
    path: '/event-suggestion',
    name: 'EventSuggestion',
    component: EventSuggestion
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/friends',
    name: 'Friends',
    component: Friends
  },
  {
    path: '/friend-info',
    name: 'FriendInfo',
    component: FriendInfo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router