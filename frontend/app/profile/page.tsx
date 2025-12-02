'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Save, User, Mail, Building2, Hash } from 'lucide-react';
import Navigation from '@/components/Navigation';

interface ProfileData {
  name: string;
  email: string;
  employeeId: string;
  department: string;
  institution: string;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData>({
    name: '',
    email: '',
    employeeId: '',
    department: '',
    institution: '',
  });
  const [isSaved, setIsSaved] = useState(false);

  const handleChange = (field: keyof ProfileData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setProfile((prev) => ({ ...prev, [field]: e.target.value }));
    setIsSaved(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In production, save to backend/localStorage
    localStorage.setItem('autoreceipt_profile', JSON.stringify(profile));
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

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
              Manage your personal information for expense claims.
            </p>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            onSubmit={handleSubmit}
            className="card space-y-6"
          >
            {/* Name Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <User className="w-4 h-4 text-[#64748B]" />
                Full Name
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={handleChange('name')}
                placeholder="John Doe"
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
                value={profile.email}
                onChange={handleChange('email')}
                placeholder="john.doe@university.edu"
                className="w-full"
              />
            </div>

            {/* Employee ID Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <Hash className="w-4 h-4 text-[#64748B]" />
                Employee ID
              </label>
              <input
                type="text"
                value={profile.employeeId}
                onChange={handleChange('employeeId')}
                placeholder="EMP-12345"
                className="w-full"
              />
            </div>

            {/* Department Field */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <Building2 className="w-4 h-4 text-[#64748B]" />
                Department
              </label>
              <input
                type="text"
                value={profile.department}
                onChange={handleChange('department')}
                placeholder="Computer Science"
                className="w-full"
              />
            </div>

            {/* Institution Selection */}
            <div>
              <label className="flex items-center gap-2 text-[#1E293B] font-medium mb-2">
                <Building2 className="w-4 h-4 text-[#64748B]" />
                University / Institution
              </label>
              <select
                value={profile.institution}
                onChange={handleChange('institution')}
                className="w-full"
              >
                <option value="">Select your institution</option>
                <option value="tu-darmstadt">TU Darmstadt</option>
                <option value="lmu-munich">LMU Munich</option>
                <option value="tu-munich">TU Munich</option>
                <option value="heidelberg">Heidelberg University</option>
                <option value="fu-berlin">FU Berlin</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Save Button */}
            <div className="pt-4">
              <button
                type="submit"
                className="btn-primary w-full relative overflow-hidden"
              >
                {isSaved ? (
                  <motion.span
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Changes Saved
                  </motion.span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Save className="w-5 h-5" />
                    Save Changes
                  </span>
                )}
              </button>
            </div>
          </motion.form>

          {/* Info Box */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-8 p-4 bg-[#F0FDFA] rounded-xl border border-[#06B6D4]/20"
          >
            <p className="text-sm text-[#0891B2]">
              <strong>💡 Tip:</strong> Your profile information will be used to pre-fill expense
              forms, saving you time on each claim.
            </p>
          </motion.div>
        </div>
      </main>
    </>
  );
}
