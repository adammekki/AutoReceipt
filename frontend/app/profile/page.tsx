'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, User, Mail, Building2, Phone, MapPin, Trash2, AlertCircle, CheckCircle } from 'lucide-react';
import Navigation from '@/components/Navigation';
import { useApp } from '@/context/AppContext';
import { clearProfile, isProfileEmpty } from '@/lib/userProfile';

export default function ProfilePage() {
  const { 
    userProfile, 
    updateUserProfile, 
    saveUserProfile, 
    isProfileLoaded,
    profileValidationErrors 
  } = useApp();
  
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved' | 'error'>('idle');
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  // Reset save status after 3 seconds
  useEffect(() => {
    if (saveStatus !== 'idle') {
      const timer = setTimeout(() => setSaveStatus('idle'), 3000);
      return () => clearTimeout(timer);
    }
  }, [saveStatus]);

  const handleChange = (field: keyof typeof userProfile) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    updateUserProfile({ [field]: e.target.value });
    setSaveStatus('idle');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const success = saveUserProfile();
    setSaveStatus(success ? 'saved' : 'error');
  };

  const handleClearProfile = () => {
    clearProfile();
    updateUserProfile({
      fullName: '',
      phoneNumber: '',
      email: '',
      postalAddress: '',
      institute: '',
    });
    setShowClearConfirm(false);
    setSaveStatus('idle');
  };

  const hasValidationErrors = Object.keys(profileValidationErrors).length > 0;
  const isEmpty = isProfileEmpty(userProfile);

  // Show loading state while profile loads from localStorage
  if (!isProfileLoaded) {
    return (
      <>
        <Navigation />
        <main className="min-h-screen pt-24 pb-12 px-6 bg-gradient-to-b from-white to-[#F8FAFC]">
          <div className="max-w-xl mx-auto">
            <div className="animate-pulse">
              <div className="h-10 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-6 bg-gray-200 rounded w-2/3 mb-10"></div>
              <div className="card space-y-6">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i}>
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-10 bg-gray-200 rounded w-full"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-24 pb-12 px-6 bg-gradient-to-b from-white to-[#F8FAFC]">
        <div className="max-w-xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-[2.5rem] font-extrabold text-[#1E293B] tracking-tight mb-2">
              Profile
            </h1>
            <p className="text-[#64748B] text-lg mb-10">
              Manage your personal information for expense claims. Your data is stored locally in your browser only.
            </p>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            onSubmit={handleSubmit}
            className="card space-y-6"
          >
            {/* Full Name Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <User className="w-4 h-4 text-[#64748B]" />
                Full Name
              </label>
              <input
                type="text"
                value={userProfile.fullName}
                onChange={handleChange('fullName')}
                placeholder="Max Mustermann"
                className="w-full"
              />
            </div>

            {/* Email Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <Mail className="w-4 h-4 text-[#64748B]" />
                Email Address
              </label>
              <input
                type="email"
                value={userProfile.email}
                onChange={handleChange('email')}
                placeholder="max.mustermann@tu-darmstadt.de"
                className={`w-full ${profileValidationErrors.email ? 'border-red-400 focus:ring-red-400' : ''}`}
              />
              {profileValidationErrors.email && (
                <p className="mt-1 text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {profileValidationErrors.email}
                </p>
              )}
            </div>

            {/* Phone Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <Phone className="w-4 h-4 text-[#64748B]" />
                Phone Number
              </label>
              <input
                type="tel"
                value={userProfile.phoneNumber}
                onChange={handleChange('phoneNumber')}
                placeholder="+49 6151 16-12345"
                className={`w-full ${profileValidationErrors.phoneNumber ? 'border-red-400 focus:ring-red-400' : ''}`}
              />
              {profileValidationErrors.phoneNumber && (
                <p className="mt-1 text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {profileValidationErrors.phoneNumber}
                </p>
              )}
            </div>

            {/* Postal Address Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <MapPin className="w-4 h-4 text-[#64748B]" />
                Postal Address
              </label>
              <textarea
                value={userProfile.postalAddress}
                onChange={handleChange('postalAddress')}
                placeholder="Musterstraße 123&#10;64289 Darmstadt"
                rows={2}
                className="w-full resize-none"
              />
              <p className="mt-1 text-xs text-[#94A3B8]">
                Street, PLZ, and City
              </p>
            </div>

            {/* Institute Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <Building2 className="w-4 h-4 text-[#64748B]" />
                Institute / Department
              </label>
              <input
                type="text"
                value={userProfile.institute}
                onChange={handleChange('institute')}
                placeholder="Institut für Informatik, TU Darmstadt"
                className="w-full"
              />
            </div>

            {/* Button Row */}
            <div className="pt-4 flex gap-3">
              {/* Save Button */}
              <button
                type="submit"
                disabled={hasValidationErrors}
                className={`btn-primary flex-1 relative overflow-hidden ${
                  hasValidationErrors ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {saveStatus === 'saved' ? (
                  <motion.span
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-center gap-2"
                  >
                    <CheckCircle className="w-5 h-5" />
                    Saved!
                  </motion.span>
                ) : saveStatus === 'error' ? (
                  <motion.span
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-center gap-2 text-red-100"
                  >
                    <AlertCircle className="w-5 h-5" />
                    Error Saving
                  </motion.span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <Save className="w-5 h-5" />
                    Save Changes
                  </span>
                )}
              </button>

              {/* Clear Button */}
              {!isEmpty && (
                <button
                  type="button"
                  onClick={() => setShowClearConfirm(true)}
                  className="px-4 py-2 text-[#64748B] hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              )}
            </div>
          </motion.form>

          {/* Clear Confirmation Modal */}
          {showClearConfirm && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4"
              onClick={() => setShowClearConfirm(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl"
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="text-lg font-semibold text-[#1E293B] mb-2">
                  Clear Profile Data?
                </h3>
                <p className="text-[#64748B] mb-6">
                  This will remove all your saved profile information from this browser.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowClearConfirm(false)}
                    className="flex-1 px-4 py-2 border border-[#E2E8F0] rounded-xl text-[#64748B] hover:bg-[#F8FAFC] transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleClearProfile}
                    className="flex-1 px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
                  >
                    Clear Data
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}

          {/* Privacy Info Box */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-8 p-4 bg-[#F0FDFA] rounded-xl border border-[#06B6D4]/20"
          >
            <p className="text-sm text-[#0891B2]">
              <strong>🔒 Privacy:</strong> Your profile data is stored only in your browser&apos;s local storage. 
              It is never sent to our servers except when submitting a reimbursement request. 
              Bank details (IBAN, BIC) are never stored.
            </p>
          </motion.div>

          {/* Prefill Info Box */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-4 p-4 bg-[#FEF3C7] rounded-xl border border-[#F59E0B]/20"
          >
            <p className="text-sm text-[#92400E]">
              <strong>💡 Tip:</strong> Your profile information will be used to pre-fill expense forms, 
              reducing manual entry. The Antrag document will fill any missing fields automatically.
            </p>
          </motion.div>
        </div>
      </main>
    </>
  );
}
