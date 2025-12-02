'use client';

import { motion } from 'framer-motion';
import { Plane, Building2, Receipt } from 'lucide-react';

interface SummaryCardProps {
  type: 'flight' | 'hotel' | 'total';
  label: string;
  amount: string;
  detail?: string;
}

export default function SummaryCard({ type, label, amount, detail }: SummaryCardProps) {
  const icons = {
    flight: Plane,
    hotel: Building2,
    total: Receipt,
  };

  const colors = {
    flight: 'from-[#06B6D4] to-[#0891B2]',
    hotel: 'from-[#8B5CF6] to-[#7C3AED]',
    total: 'from-[#1E293B] to-[#334155]',
  };

  const Icon = icons[type];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="summary-card flex items-center gap-4 cursor-default"
    >
      <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${colors[type]} flex items-center justify-center shadow-lg`}>
        <Icon className="w-7 h-7 text-white" />
      </div>
      
      <div className="flex-1">
        <p className="text-[#64748B] text-sm font-medium">{label}</p>
        <p className="text-[#1E293B] text-2xl font-bold">{amount}</p>
        {detail && <p className="text-[#94A3B8] text-xs mt-0.5">{detail}</p>}
      </div>
    </motion.div>
  );
}
