'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, RefreshCw, Check, FileText, AlertCircle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { downloadFilledForm } from '../../lib/api';

export default function CompletionScreen() {
  const { tripData, resetApp } = useApp();
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  
  const result = tripData.result;

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);
    
    try {
      const blob = await downloadFilledForm();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Reisekostenabrechnung_ausgefuellt.pdf';
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      setDownloadError(err instanceof Error ? err.message : 'Download failed');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAFBFC] to-[#F1F5F9] flex flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-xl text-center">
        {/* Success Animation */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', duration: 0.5 }}
          className="w-24 h-24 mx-auto mb-8 bg-[#10B981] rounded-full flex items-center justify-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Check className="w-12 h-12 text-white" strokeWidth={3} />
          </motion.div>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-3xl md:text-4xl font-bold text-[#1E293B] mb-4"
        >
          Your Form is Ready!
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-lg text-[#64748B] mb-10"
        >
          We&apos;ve extracted all the data from your documents and filled out your reimbursement form.
        </motion.p>

        {/* Result Summary */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0] mb-8"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-[#10B981]/10 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-[#10B981]" />
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-[#1E293B]">Reisekostenabrechnung</h3>
                <p className="text-sm text-[#64748B]">Filled and ready for download</p>
              </div>
            </div>
            
            {/* Processing Stats */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-[#E2E8F0]">
              <div className="text-center">
                <p className="text-2xl font-bold text-[#1E293B]">1</p>
                <p className="text-xs text-[#64748B]">Antrag</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-[#1E293B]">
                  {tripData.flightReceipts.length}
                </p>
                <p className="text-xs text-[#64748B]">Flight Receipts</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-[#1E293B]">
                  {tripData.hotelConferenceReceipts.length}
                </p>
                <p className="text-xs text-[#64748B]">Hotel/Conf.</p>
              </div>
            </div>

            {/* Errors if any */}
            {result.errors && result.errors.length > 0 && (
              <div className="mt-4 pt-4 border-t border-[#E2E8F0]">
                <div className="flex items-start gap-2 text-left">
                  <AlertCircle className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-[#92400E]">Some items need attention:</p>
                    <ul className="text-xs text-[#64748B] mt-1 space-y-1">
                      {result.errors.map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Download Error */}
        {downloadError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm"
          >
            {downloadError}
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
            onClick={handleDownload}
            disabled={isDownloading}
            className={`
              flex items-center justify-center gap-3 px-10 py-4 rounded-full font-medium text-lg
              transition-all duration-300 shadow-lg w-full max-w-sm
              ${isDownloading 
                ? 'bg-[#94A3B8] cursor-not-allowed' 
                : 'bg-[#10B981] hover:bg-[#059669] hover:shadow-xl hover:shadow-[#10B981]/25'
              }
              text-white
            `}
          >
            {isDownloading ? (
              <>
                <motion.div
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Download Form
              </>
            )}
          </button>

          <button
            onClick={resetApp}
            className="flex items-center gap-2 text-[#64748B] hover:text-[#1E293B] transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Start New Claim
          </button>
        </motion.div>
      </div>
    </div>
  );
}
