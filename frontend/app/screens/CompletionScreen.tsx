'use client';

import { motion } from 'framer-motion';
import { Download, RefreshCw } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import SuccessAnimation from '@/components/SuccessAnimation';
import SummaryCard from '@/components/SummaryCard';

export default function CompletionScreen() {
  const { tripData, resetApp } = useApp();
  const results = tripData.results;

  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-xl text-center">
        {/* Success Animation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="flex justify-center mb-8"
        >
          <SuccessAnimation />
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-[2.5rem] md:text-[3rem] font-extrabold text-[#1E293B] tracking-tight mb-4"
        >
          Your Form is Ready
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-lg text-[#64748B] mb-10"
        >
          We&apos;ve extracted all the data from your receipts and filled out your expense form.
        </motion.p>

        {/* Summary Cards */}
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="space-y-4 mb-10"
          >
            <SummaryCard
              type="flight"
              label="Flight Expenses"
              amount={results.flightTotal}
              detail={`${tripData.flightFiles.length} receipt(s) processed`}
            />
            <SummaryCard
              type="hotel"
              label="Hotel Expenses"
              amount={results.hotelTotal}
              detail={`${tripData.hotelFiles.length} receipt(s) processed`}
            />
            <SummaryCard
              type="total"
              label="Grand Total"
              amount={results.grandTotal}
            />
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="flex flex-col items-center gap-4"
        >
          <button
            onClick={() => {
              // In production, this would trigger the actual download
              window.alert('Download functionality will be connected to the backend API');
            }}
            className="group btn-primary text-lg px-10 py-5 w-full max-w-sm"
          >
            <Download className="w-5 h-5" />
            Download Form
          </button>

          <button
            onClick={resetApp}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Start New Claim
          </button>
        </motion.div>
      </div>
    </div>
  );
}
