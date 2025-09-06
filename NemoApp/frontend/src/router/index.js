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
// Removed ApiTester per requirement
import MyBookings from '../views/MyBookings.vue'
import ProfileCompletion from '../views/ProfileCompletion.vue'

// Pinia store access for guards
import { pinia } from '../stores'
import { useAuthStore } from '../stores/auth'

const routes = [
  // Default route will redirect based on auth in a global guard
  { path: '/', redirect: '/discover' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/signup', name: 'SignUp', component: SignUp },
  { path: '/discover', name: 'Discover', component: Discover },
  { path: '/event/:eventId', name: 'Event', component: Event, props: true },
  { path: '/event-creation', name: 'EventCreation', component: EventCreation, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/event-suggestion', name: 'EventSuggestion', component: EventSuggestion, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/friends', name: 'Friends', component: Friends, meta: { requiresAuth: true } },
  { path: '/friend-info', name: 'FriendInfo', component: FriendInfo, meta: { requiresAuth: true } },
  // Removed ApiTester route
  { path: '/my-bookings', name: 'MyBookings', component: MyBookings, meta: { requiresAuth: true } },
  { path: '/profile-completion', name: 'ProfileCompletion', component: ProfileCompletion, meta: { requiresAuth: true, allowIncompleteProfile: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guards
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore(pinia)

  // Wait for Firebase auth first emission to avoid false redirect on hard refresh
  try {
    if (typeof auth.waitForAuthReady === 'function') {
      await auth.waitForAuthReady()
    }
  } catch (_) { /* no-op */ }

  // Initialize auth from persisted storage on first navigation (verifies token with backend)
  if (!auth.isAuthenticated) {
    await auth.initializeAuth()
  }

  const isAuthed = auth.isAuthenticated
  const isAdmin = auth.isAdmin
  const profileCompleted = auth.profileCompleted

  // Only show /login to users who are not logged in
  if (to.path === '/login' && isAuthed) {
    return next('/discover')
  }

  // Require auth for routes marked with requiresAuth
  if (to.matched.some(r => r.meta?.requiresAuth)) {
    if (!isAuthed) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }
  }

  // Block all routes for first-time users until they complete profile,
  // except the dedicated profile completion route (allowIncompleteProfile flag)
  if (isAuthed && !profileCompleted) {
    const allowsIncomplete = to.matched.some(r => r.meta?.allowIncompleteProfile)
    if (!allowsIncomplete) {
      return next({ path: '/profile-completion', query: { redirect: to.fullPath } })
    }
  }

  // Enforce admin-only access for event creation
  if (to.matched.some(r => r.meta?.requiresAdmin)) {
    if (!isAdmin) {
      return next('/discover')
    }
  }

  return next()
})

export default router