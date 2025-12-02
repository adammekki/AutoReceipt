'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export default function LandingScreen() {
  const { setCurrentStep } = useApp();

  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col items-center justify-center px-6">
      <div className="max-w-3xl text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 bg-[#F0FDFA] rounded-full mb-8"
        >
          <Sparkles className="w-4 h-4 text-[#06B6D4]" />
          <span className="text-sm font-medium text-[#0891B2]">AI-Powered Automation</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-[3.5rem] md:text-[4.5rem] font-extrabold text-[#1E293B] leading-tight tracking-tight mb-6"
        >
          Reimbursement,
          <br />
          <span className="bg-gradient-to-r from-[#06B6D4] to-[#0891B2] bg-clip-text text-transparent">
            Reimagined
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-xl md:text-2xl text-[#64748B] max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          Upload your travel receipts and let our AI automatically extract the data
          and fill out your expense forms. No more manual data entry.
        </motion.p>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <button
            onClick={() => setCurrentStep('flight-upload')}
            className="group btn-primary text-lg px-10 py-5"
          >
            Start New Claim
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

        {/* Feature highlights */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {[
            {
              icon: '✈️',
              title: 'Flight Receipts',
              description: 'Upload airline confirmations and boarding passes',
            },
            {
              icon: '🏨',
              title: 'Hotel Invoices',
              description: 'Add accommodation receipts with ease',
            },
            {
              icon: '📋',
              title: 'Auto-Fill Forms',
              description: 'Download your completed expense form',
            },
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-[#1E293B] mb-2">{feature.title}</h3>
              <p className="text-[#64748B] text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
