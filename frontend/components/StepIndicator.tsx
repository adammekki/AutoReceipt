'use client';

import { motion } from 'framer-motion';

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

export default function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-center gap-3 mb-12">
      {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
        <div key={step} className="flex items-center gap-3">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: step * 0.1 }}
            className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all duration-300 ${
              step === currentStep
                ? 'bg-[#1E293B] text-white'
                : step < currentStep
                ? 'bg-[#10B981] text-white'
                : 'bg-[#F1F5F9] text-[#94A3B8]'
            }`}
          >
            {step < currentStep ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              step
            )}
          </motion.div>
          {step < totalSteps && (
            <div
              className={`w-16 h-1 rounded-full transition-all duration-300 ${
                step < currentStep ? 'bg-[#10B981]' : 'bg-[#F1F5F9]'
              }`}
            />
          )}
        </div>
      ))}
      <span className="ml-4 text-[#64748B] font-medium">
        Step {currentStep} of {totalSteps}
      </span>
    </div>
  );
}
