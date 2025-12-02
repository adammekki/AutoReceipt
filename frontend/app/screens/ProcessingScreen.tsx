'use client';

import { useEffect, useCallback } from 'react';
import { useApp } from '@/context/AppContext';
import ProcessingAnimation from '@/components/ProcessingAnimation';

interface ProcessingScreenProps {
  type: 'flight' | 'hotel';
}

const flightMessages = [
  'Analyzing Your Flight Data...',
  'Extracting dates and amounts',
  'Verifying airline codes',
  'Organizing flight segments',
  'Almost there...',
];

const hotelMessages = [
  'Organizing Your Accommodations...',
  'Extracting check-in dates',
  'Processing room charges',
  'Verifying hotel information',
  'Finalizing your form...',
];

export default function ProcessingScreen({ type }: ProcessingScreenProps) {
  const { setCurrentStep, setResults, tripData } = useApp();

  const processReceipts = useCallback(async () => {
    // Simulate processing time (in production, this would call the actual API)
    const processingTime = 4000 + Math.random() * 2000;
    
    await new Promise(resolve => setTimeout(resolve, processingTime));

    // In a real implementation, you would call the backend API here
    // For demo purposes, we'll simulate results
    const mockResults = {
      flightTotal: `€${(Math.random() * 500 + 200).toFixed(2)}`,
      hotelTotal: `€${(Math.random() * 300 + 150).toFixed(2)}`,
      grandTotal: `€${(Math.random() * 800 + 350).toFixed(2)}`,
      downloadUrl: '/api/download/filled_form.pdf',
    };

    if (type === 'flight') {
      setCurrentStep('hotel-upload');
    } else {
      setResults(mockResults);
      setCurrentStep('complete');
    }
  }, [type, setCurrentStep, setResults]);

  useEffect(() => {
    processReceipts();
  }, [processReceipts]);

  return (
    <ProcessingAnimation
      type={type}
      messages={type === 'flight' ? flightMessages : hotelMessages}
    />
  );
}
