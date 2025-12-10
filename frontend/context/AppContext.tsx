'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

// Step types for the 3-stage upload flow
export type AppStep = 
  | 'landing' 
  | 'antrag-upload'       // Step 1: Upload Dienstreiseantrag
  | 'flight-upload'       // Step 2: Upload flight receipts
  | 'hotel-upload'        // Step 3: Upload hotel/conference receipts
  | 'processing'          // Processing all documents
  | 'complete';           // Show results and download

// API response type matching backend ProcessTripResponse
export interface ProcessTripResponse {
  status: string;
  message: string;
  filled_pdf: string | null;
  errors: string[] | null;
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
  
  // Reset
  resetApp: () => void;
  
  // Processing state
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;
  processingMessage: string;
  setProcessingMessage: (message: string) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const initialTripData: TripData = {
  antragFile: null,
  flightReceipts: [],
  parkingReceipts: [],
  hotelConferenceReceipts: [],
  result: null,
};

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentStep, setCurrentStep] = useState<AppStep>('landing');
  const [tripData, setTripData] = useState<TripData>(initialTripData);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

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
        resetApp,
        isProcessing,
        setIsProcessing,
        processingMessage,
        setProcessingMessage,
        error,
        setError,
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
