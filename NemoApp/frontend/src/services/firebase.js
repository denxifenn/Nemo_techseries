// Firebase client initialization for web
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as fbSignOut
} from 'firebase/auth';
import firebaseConfig from '../../../firebase/firebase-config.js';

// Initialize app
const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);

// Helper to get current user's ID token (or null)
export async function getIdToken(forceRefresh = false) {
  try {
    const user = auth.currentUser;
    if (!user) return null;
    return await user.getIdToken(forceRefresh);
  } catch (e) {
    console.error('[firebase] getIdToken error', e);
    return null;
  }
}

// Auth helpers re-export
export { firebaseApp, auth, signInWithEmailAndPassword, createUserWithEmailAndPassword };

// Sign out wrapper
export async function signOut() {
  try {
    await fbSignOut(auth);
  } catch (e) {
    console.error('[firebase] signOut error', e);
  }
}

// Subscribe to auth state changes (optional utility)
export function onAuth(callback) {
  return onAuthStateChanged(auth, callback);
}

export default {
  firebaseApp,
  auth,
  getIdToken,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuth,
};