'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { User, FileText } from 'lucide-react';

export default function Navigation() {
  const pathname = usePathname();
  const isProfile = pathname === '/profile';

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-[#E2E8F0]"
    >
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 bg-gradient-to-br from-[#1E293B] to-[#334155] rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-[#1E293B]">AutoReceipt</span>
        </Link>

        <Link
          href="/profile"
          className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 ${
            isProfile
              ? 'bg-[#1E293B] text-white'
              : 'bg-[#F1F5F9] text-[#64748B] hover:bg-[#E2E8F0]'
          }`}
        >
          <User className="w-5 h-5" />
        </Link>
      </div>
    </motion.nav>
  );
}
