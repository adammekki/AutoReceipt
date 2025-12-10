'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Check, ArrowLeft, ArrowRight, X, Plane } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function FlightUploadScreen() {
  const { setCurrentStep, tripData, setFlightReceipts } = useApp();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>(tripData.flightReceipts);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf' || file.type.startsWith('image/')
    );
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files]);
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setUploadedFiles(prev => [...prev, ...Array.from(files)]);
    }
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  }, []);

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleContinue = () => {
    setFlightReceipts(uploadedFiles);
    setCurrentStep('hotel-upload');
  };

  const handleSkip = () => {
    setFlightReceipts([]);
    setCurrentStep('hotel-upload');
  };

  const handleBack = () => {
    setCurrentStep('antrag-upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAFBFC] to-[#F1F5F9] flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6"
      >
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-[#64748B] hover:text-[#1E293B] transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#3B82F6]/10 rounded-full text-[#3B82F6] text-sm font-medium mb-4">
            <span className="w-5 h-5 bg-[#3B82F6] rounded-full text-white text-xs flex items-center justify-center">2</span>
            Step 2 of 3
          </div>
          <h1 className="text-3xl font-bold text-[#1E293B] mb-3">
            Upload Flight Receipts
          </h1>
          <p className="text-[#64748B] max-w-md mx-auto">
            Add your flight tickets, boarding passes, and parking receipts
          </p>
        </motion.div>

        {/* Upload Area */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="w-full max-w-lg"
        >
          {/* Drag & Drop Zone */}
          <motion.div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`
              relative border-2 border-dashed rounded-2xl p-8 text-center
              transition-all duration-300 cursor-pointer mb-4
              ${dragActive 
                ? 'border-[#3B82F6] bg-[#3B82F6]/5' 
                : 'border-[#E2E8F0] bg-white hover:border-[#3B82F6]/50 hover:bg-[#FAFBFC]'
              }
            `}
          >
            <input
              type="file"
              accept=".pdf,image/*"
              multiple
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <motion.div
              animate={{ 
                scale: dragActive ? 1.1 : 1,
                y: dragActive ? -5 : 0 
              }}
              className="flex flex-col items-center"
            >
              <div className={`
                w-14 h-14 rounded-2xl flex items-center justify-center mb-3
                transition-colors duration-300
                ${dragActive ? 'bg-[#3B82F6]' : 'bg-[#F1F5F9]'}
              `}>
                <Plane className={`w-7 h-7 ${dragActive ? 'text-white' : 'text-[#64748B]'}`} />
              </div>
              <p className="text-[#1E293B] font-medium mb-1">
                {dragActive ? 'Drop files here' : 'Drag & drop files'}
              </p>
              <p className="text-[#94A3B8] text-sm">
                PDFs and images accepted • Multiple files allowed
              </p>
            </motion.div>
          </motion.div>

          {/* Uploaded Files List */}
          <AnimatePresence>
            {uploadedFiles.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-2"
              >
                {uploadedFiles.map((file, index) => (
                  <motion.div
                    key={`${file.name}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="bg-white rounded-xl p-4 shadow-sm border border-[#E2E8F0] flex items-center gap-3"
                  >
                    <div className="w-10 h-10 bg-[#10B981]/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Check className="w-5 h-5 text-[#10B981]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-[#64748B] flex-shrink-0" />
                        <span className="text-[#1E293B] font-medium truncate text-sm">
                          {file.name}
                        </span>
                      </div>
                      <p className="text-[#94A3B8] text-xs">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1.5 hover:bg-[#F1F5F9] rounded-lg transition-colors flex-shrink-0"
                    >
                      <X className="w-4 h-4 text-[#64748B]" />
                    </button>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 flex flex-col items-center gap-3"
        >
          <button
            onClick={handleContinue}
            className={`
              flex items-center gap-2 px-8 py-4 rounded-full font-medium
              transition-all duration-300 shadow-lg
              ${uploadedFiles.length > 0
                ? 'bg-[#3B82F6] text-white hover:bg-[#2563EB] hover:shadow-xl hover:shadow-[#3B82F6]/25'
                : 'bg-[#E2E8F0] text-[#94A3B8] cursor-not-allowed'
              }
            `}
            disabled={uploadedFiles.length === 0}
          >
            Continue to Hotel Receipts
            <ArrowRight className="w-5 h-5" />
          </button>
          
          <button
            onClick={handleSkip}
            className="text-[#64748B] hover:text-[#1E293B] text-sm transition-colors"
          >
            Skip this step
          </button>
        </motion.div>
      </div>
    </div>
  );
}
