'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  UserProfile, 
  EMPTY_PROFILE, 
  loadProfile, 
  saveProfile as saveProfileToStorage,
  validateProfile,
  ProfileValidationErrors 
} from '@/lib/userProfile';

// Re-export UserProfile type for convenience
export type { UserProfile, ProfileValidationErrors };

// Step types for the 3-stage upload flow
export type AppStep = 
  | 'landing' 
  | 'antrag-upload'       // Step 1: Upload Dienstreiseantrag
  | 'flight-upload'       // Step 2: Upload flight receipts
  | 'hotel-upload'        // Step 3: Upload hotel/conference receipts
  | 'processing'          // Processing all documents
  | 'verification'        // Verify AI-extracted dates, times, locations
  | 'complete';           // Show results and download

// API response type matching backend ProcessTripResponse
export interface ProcessTripResponse {
  status: string;
  message: string;
  filled_pdf: string | null;
  errors: string[] | null;
}

// Extended response for extraction phase (before verification)
export interface ExtractedDataResponse {
  status: string;
  message: string;
  session_id: string;
  hinreise: Record<string, string>;
  ruckreise: Record<string, string>;
  hotel: Record<string, string>;
  errors?: string[] | null;
}

// Trip data containing all uploaded files across steps
interface TripData {
  // Step 1: Required Antrag form
  antragFile: File | null;
  
  // Step 2: Flight-related documents
  flightReceipts: File[];
  parkingReceipts: File[];
  
  // Step 3: Hotel and conference receipts
  hotelConferenceReceipts: File[];
  
  // Processing results
  result: ProcessTripResponse | null;
  
  // Extracted data for verification
  extractedData: ExtractedDataResponse | null;
}

interface AppContextType {
  // Navigation
  currentStep: AppStep;
  setCurrentStep: (step: AppStep) => void;
  
  // Trip data
  tripData: TripData;
  
  // Step 1: Antrag
  setAntragFile: (file: File | null) => void;
  
  // Step 2: Flight documents
  setFlightReceipts: (files: File[]) => void;
  setParkingReceipts: (files: File[]) => void;
  
  // Step 3: Hotel/Conference documents
  setHotelConferenceReceipts: (files: File[]) => void;
  
  // Results
  setResult: (result: ProcessTripResponse | null) => void;
  
  // Extracted data for verification
  setExtractedData: (data: ExtractedDataResponse | null) => void;
  
  // Reset
  resetApp: () => void;
  
  // Processing state
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;
  processingMessage: string;
  setProcessingMessage: (message: string) => void;
  error: string | null;
  setError: (error: string | null) => void;

  // User Profile (client-side persistence)
  userProfile: UserProfile;
  setUserProfile: (profile: UserProfile) => void;
  updateUserProfile: (updates: Partial<UserProfile>) => void;
  saveUserProfile: () => boolean;
  isProfileLoaded: boolean;
  profileValidationErrors: ProfileValidationErrors;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const initialTripData: TripData = {
  antragFile: null,
  flightReceipts: [],
  parkingReceipts: [],
  hotelConferenceReceipts: [],
  result: null,
  extractedData: null,
};

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentStep, setCurrentStep] = useState<AppStep>('landing');
  const [tripData, setTripData] = useState<TripData>(initialTripData);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  // User Profile state (client-side persistence)
  const [userProfile, setUserProfileState] = useState<UserProfile>(EMPTY_PROFILE);
  const [isProfileLoaded, setIsProfileLoaded] = useState(false);
  const [profileValidationErrors, setProfileValidationErrors] = useState<ProfileValidationErrors>({});

  // Load user profile from localStorage on mount
  useEffect(() => {
    const storedProfile = loadProfile();
    setUserProfileState(storedProfile);
    setIsProfileLoaded(true);
  }, []);

  // Update profile with new values
  const setUserProfile = (profile: UserProfile) => {
    setUserProfileState(profile);
    // Validate on change
    const errors = validateProfile(profile);
    setProfileValidationErrors(errors);
  };

  // Partial update helper
  const updateUserProfile = (updates: Partial<UserProfile>) => {
    setUserProfileState((prev) => {
      const updated = { ...prev, ...updates };
      // Validate on change
      const errors = validateProfile(updated);
      setProfileValidationErrors(errors);
      return updated;
    });
  };

  // Save profile to localStorage
  const saveUserProfile = (): boolean => {
    const errors = validateProfile(userProfile);
    setProfileValidationErrors(errors);
    
    if (Object.keys(errors).length > 0) {
      return false;
    }
    
    return saveProfileToStorage(userProfile);
  };

  // Step 1: Antrag file
  const setAntragFile = (file: File | null) => {
    setTripData((prev) => ({ ...prev, antragFile: file }));
  };

  // Step 2: Flight documents
  const setFlightReceipts = (files: File[]) => {
    setTripData((prev) => ({ ...prev, flightReceipts: files }));
  };

  const setParkingReceipts = (files: File[]) => {
    setTripData((prev) => ({ ...prev, parkingReceipts: files }));
  };

  // Step 3: Hotel/Conference documents
  const setHotelConferenceReceipts = (files: File[]) => {
    setTripData((prev) => ({ ...prev, hotelConferenceReceipts: files }));
  };

  // Results
  const setResult = (result: ProcessTripResponse | null) => {
    setTripData((prev) => ({ ...prev, result }));
  };

  // Extracted data for verification
  const setExtractedData = (data: ExtractedDataResponse | null) => {
    setTripData((prev) => ({ ...prev, extractedData: data }));
  };

  // Reset everything
  const resetApp = () => {
    setCurrentStep('landing');
    setTripData(initialTripData);
    setIsProcessing(false);
    setProcessingMessage('');
    setError(null);
  };

  return (
    <AppContext.Provider
      value={{
        currentStep,
        setCurrentStep,
        tripData,
        setAntragFile,
        setFlightReceipts,
        setParkingReceipts,
        setHotelConferenceReceipts,
        setResult,
        setExtractedData,
        resetApp,
        isProcessing,
        setIsProcessing,
        processingMessage,
        setProcessingMessage,
        error,
        setError,
        // User Profile
        userProfile,
        setUserProfile,
        updateUserProfile,
        saveUserProfile,
        isProfileLoaded,
        profileValidationErrors,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
