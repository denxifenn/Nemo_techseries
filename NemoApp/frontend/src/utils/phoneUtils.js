/**
 * Singapore phone utilities for phone-<>email conversion with Firebase
 */

const PHONE_EMAIL_DOMAIN = 'phone.local';

export function onlyDigits(s) {
  return String(s || '').replace(/\D+/g, '');
}

export function isValidSingaporeLocal(local) {
  const d = onlyDigits(local);
  // Accept any 8-digit number as Singapore local number
  return /^[0-9]{8}$/.test(d);
}

/**
 * Normalize to E.164 for Singapore: +65XXXXXXXX
 * Accepts:
 *  - 8 digits (e.g., 91234567)
 *  - 65 + 8 digits (e.g., 6591234567)
 *  - +65 + 8 digits (e.g., +6591234567)
 */
export function formatSingaporePhone(input) {
  const raw = String(input || '').trim();
  if (!raw) throw new Error('Phone required');

  let digits = onlyDigits(raw);

  if (raw.startsWith('+')) {
    // e.g., +6591234567
    if (digits.startsWith('65')) digits = digits.slice(2);
  } else if (digits.startsWith('65') && digits.length === 10) {
    // e.g., 6591234567
    digits = digits.slice(2);
  }

  if (!isValidSingaporeLocal(digits)) {
    throw new Error('Invalid Singapore phone. Enter 8 digits.');
  }

  return `+65${digits}`;
}

/**
 * Convert phone to Firebase email alias: 6591234567@phone.local
 */
export function phoneToEmail(phone) {
  const e164 = formatSingaporePhone(phone); // +6591234567
  const local = e164.replace(/^\+/, ''); // 6591234567
  return `${local}@${PHONE_EMAIL_DOMAIN}`;
}

/**
 * Check if an email is in our phone-email format
 */
export function isPhoneEmail(email) {
  const s = String(email || '');
  return /^[0-9]{10}@phone\.local$/.test(s);
}

/**
 * Convert phone-email alias back to E.164 phone
 */
export function emailToPhone(email) {
  const s = String(email || '').trim().toLowerCase();
  if (!isPhoneEmail(s)) return null;
  const user = s.split('@')[0]; // 6591234567
  return `+${user}`;
}

export default {
  PHONE_EMAIL_DOMAIN,
  onlyDigits,
  isValidSingaporeLocal,
  formatSingaporePhone,
  phoneToEmail,
  isPhoneEmail,
  emailToPhone,
};