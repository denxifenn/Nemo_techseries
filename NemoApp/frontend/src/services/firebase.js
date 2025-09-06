// Firebase client initialization for web
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as fbSignOut
} from 'firebase/auth';
import { getStorage, ref as storageRef, uploadBytes, getDownloadURL } from 'firebase/storage';
import firebaseConfig from '../../../firebase/firebase-config.js';

// Initialize app
const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const storage = getStorage(firebaseApp);

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

// Upload helper for Storage -> returns public download URL
export async function uploadFile(path, file) {
  const ref = storageRef(storage, path);
  await uploadBytes(ref, file);
  return await getDownloadURL(ref);
}

// Auth helpers re-export
export { firebaseApp, auth, storage, storageRef, uploadBytes, getDownloadURL, signInWithEmailAndPassword, createUserWithEmailAndPassword };

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
  storage,
  getIdToken,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuth,
};