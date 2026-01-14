/**
 * User profile types and utilities for client-side persistence.
 */

export interface UserProfile {
  fullName: string;
  phoneNumber: string;
  email: string;
  postalAddress: string;
  institute: string;
}

export interface ProfileValidationErrors {
  fullName?: string;
  phoneNumber?: string;
  email?: string;
  postalAddress?: string;
  institute?: string;
}

export const EMPTY_PROFILE: UserProfile = {
  fullName: '',
  phoneNumber: '',
  email: '',
  postalAddress: '',
  institute: '',
};

const PROFILE_STORAGE_KEY = 'autoreceipt_user_profile';

/**
 * Load user profile from localStorage.
 */
export function loadProfile(): UserProfile | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const stored = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored) as UserProfile;
    }
  } catch (e) {
    console.error('Error loading profile from localStorage:', e);
  }
  return null;
}

/**
 * Save user profile to localStorage.
 */
export function saveProfile(profile: UserProfile): boolean {
  if (typeof window === 'undefined') return false;
  
  try {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
    return true;
  } catch (e) {
    console.error('Error saving profile to localStorage:', e);
    return false;
  }
}

/**
 * Clear user profile from localStorage.
 */
export function clearProfile(): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.removeItem(PROFILE_STORAGE_KEY);
  } catch (e) {
    console.error('Error clearing profile from localStorage:', e);
  }
}

/**
 * Check if a profile is empty (all fields are empty strings).
 */
export function isProfileEmpty(profile: UserProfile): boolean {
  return Object.values(profile).every(value => !value || value.trim() === '');
}

/**
 * Validate profile fields.
 * Returns an object with error messages for invalid fields.
 */
export function validateProfile(profile: UserProfile): ProfileValidationErrors {
  const errors: ProfileValidationErrors = {};
  
  // Email validation
  if (profile.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profile.email)) {
    errors.email = 'Please enter a valid email address';
  }
  
  // Phone validation (basic)
  if (profile.phoneNumber && !/^[\d\s\-+()]{6,}$/.test(profile.phoneNumber)) {
    errors.phoneNumber = 'Please enter a valid phone number';
  }
  
  return errors;
}
