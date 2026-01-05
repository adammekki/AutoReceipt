'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useApp } from '../../context/AppContext';
import { submitVerifiedData } from '../../lib/api';
import { 
  VerifiableField, 
  VerificationData,
  initializeVerificationData,
  validateField,
  areAllFieldsValid,
  toBackendFormat,
  HINREISE_VERIFIABLE_FIELDS,
  RUCKREISE_VERIFIABLE_FIELDS,
  HOTEL_VERIFIABLE_FIELDS,
} from '../../lib/verification';
import { 
  Check, 
  AlertCircle, 
  Calendar, 
  Clock, 
  MapPin, 
  Plane, 
  Building2, 
  ChevronDown,
  ChevronUp,
  Loader2
} from 'lucide-react';

interface FieldInputProps {
  field: VerifiableField;
  onChange: (value: string) => void;
  error: string | null;
}

function FieldInput({ field, onChange, error }: FieldInputProps) {
  const icon = useMemo(() => {
    switch (field.category) {
      case 'date': return <Calendar className="w-4 h-4 text-[#64748B]" />;
      case 'time': return <Clock className="w-4 h-4 text-[#64748B]" />;
      case 'location': return <MapPin className="w-4 h-4 text-[#64748B]" />;
    }
  }, [field.category]);

  return (
    <div className="space-y-1">
      <label className="flex items-center gap-2 text-sm font-medium text-[#1E293B]">
        {icon}
        {field.label}
      </label>
      <div className="relative">
        <input
          type="text"
          value={field.verifiedValue}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          className={`w-full px-3 py-2 text-sm border rounded-lg transition-colors
            ${error 
              ? 'border-red-400 focus:ring-red-400 focus:border-red-400' 
              : 'border-[#E2E8F0] focus:ring-[#3B82F6] focus:border-[#3B82F6]'
            }
            ${field.extractedValue !== field.verifiedValue ? 'bg-[#FEF3C7]/30' : 'bg-white'}
          `}
        />
        {field.extractedValue !== field.verifiedValue && (
          <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-[#92400E] bg-[#FEF3C7] px-1.5 py-0.5 rounded">
            edited
          </span>
        )}
      </div>
      {error && (
        <p className="text-xs text-red-500 flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          {error}
        </p>
      )}
      {field.extractedValue && field.extractedValue !== field.verifiedValue && (
        <p className="text-xs text-[#64748B]">
          AI extracted: <span className="font-mono">{field.extractedValue}</span>
        </p>
      )}
    </div>
  );
}

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  fields: VerifiableField[];
  onFieldChange: (key: string, value: string) => void;
  errors: Record<string, string | null>;
  defaultOpen?: boolean;
}

function Section({ title, icon, fields, onFieldChange, errors, defaultOpen = true }: SectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  const hasErrors = Object.values(errors).some(e => e !== null);
  const hasEdits = fields.some(f => f.extractedValue !== f.verifiedValue);

  // Filter to only show fields that have extracted values
  const fieldsWithData = fields.filter(f => f.extractedValue);
  
  if (fieldsWithData.length === 0) {
    return null; // Don't show empty sections
  }

  return (
    <div className="border border-[#E2E8F0] rounded-xl overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between bg-[#F8FAFC] hover:bg-[#F1F5F9] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white rounded-lg shadow-sm">
            {icon}
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-[#1E293B]">{title}</h3>
            <p className="text-xs text-[#64748B]">
              {fieldsWithData.length} field{fieldsWithData.length !== 1 ? 's' : ''} to verify
              {hasEdits && <span className="text-[#92400E] ml-2">• edited</span>}
              {hasErrors && <span className="text-red-500 ml-2">• has errors</span>}
            </p>
          </div>
        </div>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-[#64748B]" />
        ) : (
          <ChevronDown className="w-5 h-5 text-[#64748B]" />
        )}
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 grid gap-4 sm:grid-cols-2">
              {fieldsWithData.map((field) => (
                <FieldInput
                  key={field.key}
                  field={field}
                  onChange={(value) => onFieldChange(field.key, value)}
                  error={errors[field.key]}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function VerificationScreen() {
  const { tripData, setCurrentStep, setResult, setError } = useApp();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Initialize verification data from extracted data
  const [verificationData, setVerificationData] = useState<VerificationData>(() => {
    if (tripData.extractedData) {
      // The backend returns hinreise, ruckreise, hotel at the top level
      return initializeVerificationData({
        hinreise: tripData.extractedData.hinreise || {},
        ruckreise: tripData.extractedData.ruckreise || {},
        hotel: tripData.extractedData.hotel || {},
      });
    }
    // Fallback empty state
    return {
      hinreise: [],
      ruckreise: [],
      hotel: [],
    };
  });

  // Compute validation errors for all fields
  const errors = useMemo(() => {
    const allFields = [
      ...verificationData.hinreise,
      ...verificationData.ruckreise,
      ...verificationData.hotel,
    ];
    
    const errorMap: Record<string, string | null> = {};
    for (const field of allFields) {
      errorMap[field.key] = validateField(field);
    }
    return errorMap;
  }, [verificationData]);

  // Check if form is valid
  const isFormValid = useMemo(() => {
    const allFields = [
      ...verificationData.hinreise,
      ...verificationData.ruckreise,
      ...verificationData.hotel,
    ];
    return areAllFieldsValid(allFields);
  }, [verificationData]);

  // Update a single field
  const updateField = (section: 'hinreise' | 'ruckreise' | 'hotel', key: string, value: string) => {
    setVerificationData(prev => ({
      ...prev,
      [section]: prev[section].map(field => 
        field.key === key 
          ? { ...field, verifiedValue: value, isVerified: true }
          : field
      ),
    }));
  };

  // Accept all values as-is
  const handleAcceptAll = () => {
    setVerificationData(prev => ({
      hinreise: prev.hinreise.map(f => ({ ...f, isVerified: true })),
      ruckreise: prev.ruckreise.map(f => ({ ...f, isVerified: true })),
      hotel: prev.hotel.map(f => ({ ...f, isVerified: true })),
    }));
  };

  // Submit verified data
  const handleSubmit = async () => {
    if (!isFormValid) return;
    
    setIsSubmitting(true);
    try {
      const sessionId = tripData.extractedData?.session_id;
      if (!sessionId) {
        throw new Error('No session ID found');
      }

      const backendData = toBackendFormat(verificationData);
      const payload = {
        session_id: sessionId,
        hinreise: backendData.hinreise,
        ruckreise: backendData.ruckreise,
        hotel: backendData.hotel,
      };

      const result = await submitVerifiedData(payload);
      
      if (result.status === 'ok') {
        setResult(result);
        setCurrentStep('complete');
      } else {
        setError(result.message || 'Failed to generate PDF');
        setCurrentStep('landing');
      }
    } catch (err) {
      console.error('Verification submission error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setCurrentStep('landing');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Count total fields with data
  const totalFields = [
    ...verificationData.hinreise,
    ...verificationData.ruckreise,
    ...verificationData.hotel,
  ].filter(f => f.extractedValue).length;

  const errorCount = Object.values(errors).filter(e => e !== null).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAFBFC] to-[#F1F5F9] py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="w-16 h-16 bg-[#3B82F6]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-[#3B82F6]" />
          </div>
          <h1 className="text-2xl font-bold text-[#1E293B] mb-2">
            Verify Extracted Data
          </h1>
          <p className="text-[#64748B]">
            Please review and correct the AI-extracted dates, times, and locations below.
          </p>
        </motion.div>

        {/* Info Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-[#F0FDFA] border border-[#06B6D4]/20 rounded-xl p-4 mb-6"
        >
          <p className="text-sm text-[#0891B2]">
            <strong>💡 Tip:</strong> Only dates, times, and locations are shown for verification. 
            Prices and other numeric values have been extracted automatically.
          </p>
        </motion.div>

        {/* Verification Sections */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4 mb-8"
        >
          <Section
            title="Outbound Journey (Hinreise)"
            icon={<Plane className="w-5 h-5 text-[#3B82F6]" />}
            fields={verificationData.hinreise}
            onFieldChange={(key, value) => updateField('hinreise', key, value)}
            errors={errors}
          />
          
          <Section
            title="Return Journey (Rückreise)"
            icon={<Plane className="w-5 h-5 text-[#10B981] rotate-180" />}
            fields={verificationData.ruckreise}
            onFieldChange={(key, value) => updateField('ruckreise', key, value)}
            errors={errors}
          />
          
          <Section
            title="Hotel & Conference"
            icon={<Building2 className="w-5 h-5 text-[#8B5CF6]" />}
            fields={verificationData.hotel}
            onFieldChange={(key, value) => updateField('hotel', key, value)}
            errors={errors}
            defaultOpen={false}
          />
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-3"
        >
          {errorCount > 0 && (
            <div className="flex items-center justify-center gap-2 text-red-500 text-sm mb-2">
              <AlertCircle className="w-4 h-4" />
              <span>{errorCount} validation error{errorCount !== 1 ? 's' : ''} found</span>
            </div>
          )}
          
          <div className="flex gap-3">
            <button
              onClick={handleAcceptAll}
              disabled={isSubmitting}
              className="flex-1 px-4 py-3 border border-[#E2E8F0] rounded-xl text-[#64748B] hover:bg-[#F8FAFC] transition-colors disabled:opacity-50"
            >
              Accept All As-Is
            </button>
            <button
              onClick={handleSubmit}
              disabled={!isFormValid || isSubmitting}
              className="flex-1 px-4 py-3 bg-[#3B82F6] text-white rounded-xl hover:bg-[#2563EB] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating PDF...
                </>
              ) : (
                <>
                  <Check className="w-5 h-5" />
                  Confirm & Generate PDF
                </>
              )}
            </button>
          </div>
          
          <p className="text-center text-xs text-[#94A3B8]">
            {totalFields} fields extracted • Your verified values will be used in the final form
          </p>
        </motion.div>
      </div>
    </div>
  );
}
