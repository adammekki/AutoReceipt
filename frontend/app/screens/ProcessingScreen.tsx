'use client';

import { useEffect, useCallback, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { useApp } from '../../context/AppContext';
import { processTrip } from '../../lib/api';

const processingMessages = [
  'Analyzing your documents...',
  'Extracting travel information...',
  'Processing flight receipts...',
  'Processing hotel receipts...',
  'Filling out your form...',
  'Almost there...',
];

const funFacts = [
  "Did you know? Penguins propose to their mates with a pebble 🐧",
  "Did you know? Honey never spoils — 3,000-year-old honey was found edible in Egyptian tombs 🍯",
  "Did you know? Octopuses have three hearts and blue blood 🐙",
  "Did you know? A group of flamingos is called a 'flamboyance' 🦩",
  "Did you know? Bananas are berries, but strawberries aren't 🍌",
  "Did you know? The Eiffel Tower grows about 6 inches in summer due to heat expansion 🗼",
  "Did you know? Cows have best friends and get stressed when separated 🐄",
  "Did you know? A day on Venus is longer than a year on Venus 🪐",
  "Did you know? Wombat poop is cube-shaped 🦘",
  "Did you know? The shortest war in history lasted 38 minutes ⚔️",
  "Did you know? Scotland's national animal is the unicorn 🦄",
  "Did you know? There are more trees on Earth than stars in the Milky Way 🌳",
  "Did you know? Sharks existed before trees 🦈",
  "Did you know? A jiffy is an actual unit of time — 1/100th of a second ⏱️",
  "Did you know? The inventor of the Pringles can is buried in one 🥔",
];

export default function ProcessingScreen() {
  const { setCurrentStep, tripData, setResult, setError } = useApp();
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const hasStartedProcessing = useRef(false);

  // Cycle through messages
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex(prev => (prev + 1) % processingMessages.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Cycle through fun facts every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex(prev => (prev + 1) % funFacts.length);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Animate progress
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return prev;
        return prev + Math.random() * 5;
      });
    }, 300);
    return () => clearInterval(interval);
  }, []);

  const processDocuments = useCallback(async () => {
    try {
      if (!tripData.antragFile) {
        setError('Dienstreiseantrag is required');
        setCurrentStep('antrag-upload');
        return;
      }

      // Combine all receipts: flight + hotel/conference
      const allReceipts = [
        ...tripData.flightReceipts,
        ...tripData.hotelConferenceReceipts,
      ];

      const response = await processTrip(
        tripData.antragFile,
        tripData.flightReceipts,
        tripData.hotelConferenceReceipts
      );

      // Backend returns status: "ok" on success
      if (response.status === 'ok') {
        setResult(response);
        setProgress(100);
        // Small delay to show completion
        setTimeout(() => {
          setCurrentStep('complete');
        }, 500);
      } else {
        setError(response.message || 'Processing failed');
        setCurrentStep('landing');
      }
    } catch (err) {
      console.error('Processing error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setCurrentStep('landing');
    }
  }, [tripData, setResult, setError, setCurrentStep]);

  useEffect(() => {
    // Only process once - prevent infinite loop from dependency changes
    if (hasStartedProcessing.current) return;
    hasStartedProcessing.current = true;
    processDocuments();
  }, [processDocuments]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAFBFC] to-[#F1F5F9] flex flex-col items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center max-w-md"
      >
        {/* Animated Icon */}
        <div className="relative w-24 h-24 mx-auto mb-8">
          {/* Outer spinning ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-[#E2E8F0]"
            style={{ borderTopColor: '#3B82F6' }}
            animate={{ rotate: 360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
          />
          {/* Inner pulsing circle */}
          <motion.div
            className="absolute inset-3 bg-[#3B82F6]/10 rounded-full flex items-center justify-center"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <motion.div
              className="w-8 h-8 bg-[#3B82F6] rounded-lg"
              animate={{ rotate: [0, 180, 360] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            />
          </motion.div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-[#1E293B] mb-3">
          Processing your documents...
        </h2>

        <p className="text-[#64748B] mb-6">
          This usually takes a few minutes. Please don't close this page.
        </p>

        {/* Fun Fact */}
        <motion.div
          key={messageIndex}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="bg-[#FEF3C7] text-[#92400E] px-4 py-3 rounded-xl mb-8 text-sm font-medium"
        >
          {funFacts[messageIndex]}
        </motion.div>

        {/* Progress Bar */}
        <div className="w-full max-w-xs mx-auto">
          <div className="h-2 bg-[#E2E8F0] rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-[#3B82F6] to-[#10B981] rounded-full"
              initial={{ width: '0%' }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <p className="text-[#94A3B8] text-sm mt-2">
            {Math.round(progress)}% complete
          </p>
        </div>

        {/* Document Summary */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0]"
        >
          <h3 className="text-[#1E293B] font-semibold mb-4">Processing Documents</h3>
          <div className="space-y-3 text-left">
            <div className="flex items-center justify-between">
              <span className="text-[#64748B] text-sm">Dienstreiseantrag</span>
              <span className="text-[#10B981] text-sm font-medium">
                {tripData.antragFile ? '✓' : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#64748B] text-sm">Flight Receipts</span>
              <span className="text-[#1E293B] text-sm font-medium">
                {tripData.flightReceipts.length} files
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#64748B] text-sm">Hotel/Conference Receipts</span>
              <span className="text-[#1E293B] text-sm font-medium">
                {tripData.hotelConferenceReceipts.length} files
              </span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
