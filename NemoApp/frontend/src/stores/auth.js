import { defineStore } from 'pinia';
import { auth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, getIdToken } from '../services/firebase';
import { updateProfile } from 'firebase/auth';
import api from '../services/api';
import { formatSingaporePhone, phoneToEmail } from '../utils/phoneUtils';

// Auth readiness synchronization across app refresh
let _authReadyResolved = false;
let _authReadyPromise = null;
let _resolveAuthReady = null;
function _getAuthReadyPromise() {
  if (!_authReadyPromise) {
    _authReadyPromise = new Promise((resolve) => {
      _resolveAuthReady = resolve;
    });
  }
  return _authReadyPromise;
}
function _resolveAuthReadyOnce() {
  if (!_authReadyResolved) {
    _authReadyResolved = true;
    if (_resolveAuthReady) {
      _resolveAuthReady(true);
    }
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    profileCompleted: false,
    isAdmin: false,
    loading: false,
    error: null,
    token: null
  }),

  getters: {
    currentUser: (state) => state.user,
    canAccessAdmin: (state) => state.isAdmin,
    needsProfileCompletion: (state) => state.isAuthenticated && !state.profileCompleted,
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    async login(phone, password) {
      this.loading = true;
      this.error = null;

      try {
        // Format phone and convert to email
        const formatted = formatSingaporePhone(phone);
        const emailAlias = phoneToEmail(formatted);

        // Firebase authentication (authoritative)
        const userCredential = await signInWithEmailAndPassword(auth, emailAlias, password);

        // Get ID token
        const token = await userCredential.user.getIdToken();
        this.token = token;

        // Try backend handshake, but do NOT fail login if unreachable
        let userData = null;
        let backendSynced = false;
        try {
          const response = await api.backendLoginWithIdToken(token, { phoneNumber: formatted });
          if (response?.data?.success) {
            userData = response.data.user;
            backendSynced = true;
          }
        } catch (e) {
          // Network/backend error - proceed with Firebase session to avoid false "Login failed" UX
          console.warn('[auth] backend login failed, proceeding with Firebase session', e);
        }

        if (!userData) {
          const u = userCredential.user;
          userData = {
            uid: u.uid,
            phoneNumber: formatted,
            name: u.displayName || '',
            role: 'user'
          };
        }

        this.user = userData;
        this.isAuthenticated = true;
        this.isAdmin = userData.role === 'admin';

        // Profile completion may still require backend; ignore transient errors
        try { await this.checkProfileCompletion(); } catch (_) {}

        // Persist Firebase token & basic user to keep session across refresh
        try {
          localStorage.setItem('authToken', token);
          localStorage.setItem('user', JSON.stringify(userData));
        } catch {}

        return { success: true, backendSynced };
      } catch (error) {
        this.error = error.message;
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },

    async signup(phone, password, firstName, lastName, finNumber) {
      this.loading = true;
      this.error = null;

      try {
        // Format phone and convert to email
        const formatted = formatSingaporePhone(phone);
        const emailAlias = phoneToEmail(formatted);

        // Create user in Firebase
        const userCredential = await createUserWithEmailAndPassword(auth, emailAlias, password);

        // Update display name
        const displayName = `${firstName} ${lastName}`.trim();
        if (displayName) {
          try { await updateProfile(userCredential.user, { displayName }); } catch (e) { console.warn('updateProfile failed:', e); }
        }

        // Get ID token
        const token = await userCredential.user.getIdToken();
        this.token = token;

        // Try backend provisioning; do not fail signup if backend is unreachable
        let userData = null;
        let backendSynced = false;
        try {
          const response = await api.backendLoginWithIdToken(token, {
            phoneNumber: formatted,
            name: displayName || undefined,
            finNumber: finNumber
          });
          if (response?.data?.success) {
            userData = response.data.user;
            backendSynced = true;
          }
        } catch (e) {
          console.warn('[auth] backend provisioning failed, proceeding with Firebase session', e);
        }

        if (!userData) {
          const u = userCredential.user;
          userData = {
            uid: u.uid,
            phoneNumber: formatted,
            name: displayName || u.displayName || '',
            role: 'user'
          };
        }

        this.user = userData;
        this.isAuthenticated = true;
        this.isAdmin = userData.role === 'admin';
        this.profileCompleted = false;

        try {
          localStorage.setItem('authToken', token);
          localStorage.setItem('user', JSON.stringify(userData));
        } catch {}

        return { success: true, backendSynced };
      } catch (error) {
        this.error = error.message;
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await signOut(auth);
        this.user = null;
        this.isAuthenticated = false;
        this.profileCompleted = false;
        this.isAdmin = false;
        this.token = null;
        this.error = null;
        
        // Clear localStorage
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        
        return { success: true };
      } catch (error) {
        this.error = error.message;
        return { success: false, error: error.message };
      }
    },

    async checkProfileCompletion() {
      try {
        const response = await api.get('/api/profile/completion-status');
        if (response.data.success) {
          this.profileCompleted = response.data.status.profileCompleted;
          return response.data.status;
        }
      } catch (error) {
        console.error('Failed to check profile completion:', error);
        return null;
      }
    },

    async updateProfile(profileData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.put('/api/profile', profileData);
        if (response.data.success) {
          // Update local user data
          if (this.user) {
            this.user = { ...this.user, ...response.data.updated };
          }
          this.profileCompleted = response.data.profileCompleted;
          
          // Update localStorage
          localStorage.setItem('user', JSON.stringify(this.user));
          
          return { success: true, data: response.data };
        }
      } catch (error) {
        this.error = error.message;
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },

    async fetchProfile() {
      try {
        const response = await api.get('/api/profile');
        if (response.data.success) {
          const profile = response.data.profile;
          this.user = {
            ...this.user,
            ...profile
          };
          this.profileCompleted = profile.profileCompleted;
          this.isAdmin = profile.role === 'admin';
          
          // Update localStorage
          localStorage.setItem('user', JSON.stringify(this.user));
          
          return { success: true, profile };
        }
      } catch (error) {
        return { success: false, error: error.message };
      }
    },

    // Local-only session clear (no Firebase signOut) to avoid UX flicker on transient verify failures
    clearSessionLocal() {
      this.user = null;
      this.isAuthenticated = false;
      this.profileCompleted = false;
      this.isAdmin = false;
      this.token = null;
      this.error = null;
      try {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
      } catch {}
    },

    // Initialize auth state from localStorage
    async initializeAuth() {
      const storedToken = localStorage.getItem('authToken');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedUser) {
        // Provisionally trust local state so the UI doesn't flicker when backend is unreachable
        try {
          const parsed = JSON.parse(storedUser);
          this.token = storedToken;
          this.user = parsed;
          this.isAuthenticated = true;
          this.isAdmin = parsed?.role === 'admin';
        } catch {
          // parsing failed; treat as no session
          this.clearSessionLocal();
          return false;
        }

        try {
          // Best-effort verification; only clear session on explicit invalid (401/invalid)
          const response = await api.get('/api/auth/verify');
          if (response?.data?.valid) {
            try { await this.checkProfileCompletion(); } catch (_) {}
            return true;
          }

          // Explicit invalid -> clear local session
          this.clearSessionLocal();
          return false;
        } catch (error) {
          // Network/temporary error -> keep local session to avoid false logouts
          // Optionally log for diagnostics
          console.warn('[auth] verify failed (network), keeping local session', error?.message || error);
          return true;
        }
      }
      return false;
    },

    // Clear error
    clearError() {
      this.error = null;
    },

    // Wait for Firebase onAuthStateChanged first emission
    waitForAuthReady() {
      return _getAuthReadyPromise();
    },

    // Mark auth ready (call from main.js on first onAuth emission)
    markAuthReady() {
      _resolveAuthReadyOnce();
    }
  }
});