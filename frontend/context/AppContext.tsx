'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

export type AppStep = 'landing' | 'flight-upload' | 'flight-processing' | 'hotel-upload' | 'hotel-processing' | 'complete';

interface TripData {
  flightFiles: File[];
  hotelFiles: File[];
  results?: {
    flightTotal: string;
    hotelTotal: string;
    grandTotal: string;
    downloadUrl?: string;
  };
}

interface AppContextType {
  currentStep: AppStep;
  setCurrentStep: (step: AppStep) => void;
  tripData: TripData;
  setFlightFiles: (files: File[]) => void;
  setHotelFiles: (files: File[]) => void;
  setResults: (results: TripData['results']) => void;
  resetApp: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const initialTripData: TripData = {
  flightFiles: [],
  hotelFiles: [],
  results: undefined,
};

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentStep, setCurrentStep] = useState<AppStep>('landing');
  const [tripData, setTripData] = useState<TripData>(initialTripData);

  const setFlightFiles = (files: File[]) => {
    setTripData((prev) => ({ ...prev, flightFiles: files }));
  };

  const setHotelFiles = (files: File[]) => {
    setTripData((prev) => ({ ...prev, hotelFiles: files }));
  };

  const setResults = (results: TripData['results']) => {
    setTripData((prev) => ({ ...prev, results }));
  };

  const resetApp = () => {
    setCurrentStep('landing');
    setTripData(initialTripData);
  };

  return (
    <AppContext.Provider
      value={{
        currentStep,
        setCurrentStep,
        tripData,
        setFlightFiles,
        setHotelFiles,
        setResults,
        resetApp,
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
