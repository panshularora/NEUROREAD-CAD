/**
 * Learning Mode: dashboard with 4 feature cards + module pages.
 * Dark theme, soft orange (clay) accents, Framer Motion, dyslexia-friendly.
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LearningEngine from './learning/LearningEngine';

export default function LearningMode({ active, childId = 'demo-user-001' }) {
  const [view, setView] = useState('dashboard'); // 'dashboard' | 'phonics' | 'spelling' | 'comprehension' | 'reading'

  const openModule = (module) => {
    setView(module);
  };

  const backToDashboard = () => {
    setView('dashboard');
  };

  return (
    <div
      id="content-learning"
      className={`col-start-1 row-start-1 transition-all duration-700 ease-spring ${
        active ? 'opacity-100 translate-y-0 z-10' : 'opacity-0 translate-y-8 pointer-events-none z-0'
      }`}
    >
      <div className="bg-charcoal rounded-[3rem] p-8 md:p-14 shadow-2xl relative overflow-hidden min-h-[480px]">
        <div className="absolute inset-0 z-0 bg-moss/5 mix-blend-multiply border border-cream/5 rounded-[3rem]" />
        <div className="relative z-10">
          <AnimatePresence mode="wait">
            <LearningEngine childProfile={{ child_id: childId, age: 6 }} />
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
