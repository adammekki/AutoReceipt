'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import StepIndicator from '@/components/StepIndicator';
import FileUpload from '@/components/FileUpload';

export default function HotelUploadScreen() {
  const { tripData, setHotelFiles, setCurrentStep } = useApp();

  const handleContinue = () => {
    setCurrentStep('hotel-processing');
  };

  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col items-center px-6 py-12">
      <div className="w-full max-w-2xl">
        <StepIndicator currentStep={2} totalSteps={2} />

        <FileUpload
          title="Upload Hotel Receipts"
          description="Add your hotel invoices and accommodation receipts. We'll organize all your accommodation expenses."
          accept=".pdf,.png,.jpg,.jpeg"
          multiple={true}
          files={tripData.hotelFiles}
          onFilesChange={setHotelFiles}
        />

        {/* Continue Button */}
        <AnimatePresence>
          {tripData.hotelFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="fixed bottom-8 left-0 right-0 flex justify-center px-6"
            >
              <button
                onClick={handleContinue}
                className="group btn-primary shadow-2xl shadow-[#1E293B]/20"
              >
                Process All Receipts
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Skip Option */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-8"
        >
          <button
            onClick={() => setCurrentStep('hotel-processing')}
            className="btn-secondary"
          >
            Skip hotel receipts
          </button>
        </motion.div>
      </div>
    </div>
  );
}
