'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Check, ArrowLeft, ArrowRight, X } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function AntragUploadScreen() {
  const { setCurrentStep, tripData, setAntragFile } = useApp();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(tripData.antragFile);

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

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        setUploadedFile(file);
      }
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      setUploadedFile(files[0]);
    }
  }, []);

  const removeFile = () => {
    setUploadedFile(null);
  };

  const handleContinue = () => {
    if (uploadedFile) {
      setAntragFile(uploadedFile);
      setCurrentStep('flight-upload');
    }
  };

  const handleBack = () => {
    setCurrentStep('landing');
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
            <span className="w-5 h-5 bg-[#3B82F6] rounded-full text-white text-xs flex items-center justify-center">1</span>
            Step 1 of 3
          </div>
          <h1 className="text-3xl font-bold text-[#1E293B] mb-3">
            Upload Dienstreiseantrag
          </h1>
          <p className="text-[#64748B] max-w-md mx-auto">
            Start by uploading your approved travel request form (Dienstreiseantrag)
          </p>
        </motion.div>

        {/* Upload Area */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="w-full max-w-lg"
        >
          <AnimatePresence mode="wait">
            {!uploadedFile ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`
                  relative border-2 border-dashed rounded-2xl p-12 text-center
                  transition-all duration-300 cursor-pointer
                  ${dragActive 
                    ? 'border-[#3B82F6] bg-[#3B82F6]/5' 
                    : 'border-[#E2E8F0] bg-white hover:border-[#3B82F6]/50 hover:bg-[#FAFBFC]'
                  }
                `}
              >
                <input
                  type="file"
                  accept=".pdf"
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
                    w-16 h-16 rounded-2xl flex items-center justify-center mb-4
                    transition-colors duration-300
                    ${dragActive ? 'bg-[#3B82F6]' : 'bg-[#F1F5F9]'}
                  `}>
                    <Upload className={`w-8 h-8 ${dragActive ? 'text-white' : 'text-[#64748B]'}`} />
                  </div>
                  <p className="text-[#1E293B] font-medium mb-1">
                    {dragActive ? 'Drop your file here' : 'Drag & drop your PDF'}
                  </p>
                  <p className="text-[#94A3B8] text-sm">
                    or click to browse
                  </p>
                </motion.div>
              </motion.div>
            ) : (
              <motion.div
                key="file"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0]"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#10B981]/10 rounded-xl flex items-center justify-center">
                    <Check className="w-6 h-6 text-[#10B981]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <FileText className="w-4 h-4 text-[#64748B]" />
                      <span className="text-[#1E293B] font-medium truncate">
                        {uploadedFile.name}
                      </span>
                    </div>
                    <p className="text-[#94A3B8] text-sm">
                      {(uploadedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={removeFile}
                    className="p-2 hover:bg-[#F1F5F9] rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-[#64748B]" />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Continue Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <button
            onClick={handleContinue}
            disabled={!uploadedFile}
            className={`
              flex items-center gap-2 px-8 py-4 rounded-full font-medium
              transition-all duration-300 shadow-lg
              ${uploadedFile
                ? 'bg-[#3B82F6] text-white hover:bg-[#2563EB] hover:shadow-xl hover:shadow-[#3B82F6]/25'
                : 'bg-[#E2E8F0] text-[#94A3B8] cursor-not-allowed'
              }
            `}
          >
            Continue to Flight Receipts
            <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
