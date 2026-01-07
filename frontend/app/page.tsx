'use client';

import { useApp } from '@/context/AppContext';
import { AnimatePresence, motion } from 'framer-motion';
import LandingScreen from './screens/LandingScreen';
import AntragUploadScreen from './screens/AntragUploadScreen';
import FlightUploadScreen from './screens/FlightUploadScreen';
import HotelUploadScreen from './screens/HotelUploadScreen';
import ProcessingScreen from './screens/ProcessingScreen';
import VerificationScreen from './screens/VerificationScreen';
import CompletionScreen from './screens/CompletionScreen';
import Navigation from '@/components/Navigation';

const pageVariants = {
  initial: { opacity: 0, scale: 0.98 },
  enter: { opacity: 1, scale: 1, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] as const } },
  exit: { opacity: 0, scale: 0.98, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] as const } },
};

export default function Home() {
  const { currentStep } = useApp();

  const renderScreen = () => {
    switch (currentStep) {
      case 'landing':
        return <LandingScreen key="landing" />;
      case 'antrag-upload':
        return <AntragUploadScreen key="antrag-upload" />;
      case 'flight-upload':
        return <FlightUploadScreen key="flight-upload" />;
      case 'hotel-upload':
        return <HotelUploadScreen key="hotel-upload" />;
      case 'processing':
        return <ProcessingScreen key="processing" />;
      case 'verification':
        return <VerificationScreen key="verification" />;
      case 'complete':
        return <CompletionScreen key="complete" />;
      default:
        return <LandingScreen key="landing" />;
    }
  };

  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-20">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            variants={pageVariants}
            initial="initial"
            animate="enter"
            exit="exit"
          >
            {renderScreen()}
          </motion.div>
        </AnimatePresence>
      </main>
    </>
  );
}
