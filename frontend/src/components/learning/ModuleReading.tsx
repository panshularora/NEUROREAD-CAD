/**
 * Guided Reading: word-by-word highlighting, adjustable speed, tap word → hear pronunciation.
 */
import React, { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

interface ModuleReadingProps {
  onBack: () => void;
  childId: string;
}

const SENTENCE = 'The cat sat on the mat.';

export default function ModuleReading({ onBack, childId }: ModuleReadingProps) {
  const words = SENTENCE.split(/\s+/);
  const [highlightIndex, setHighlightIndex] = useState<number | null>(null);
  const [speed, setSpeed] = useState(1);

  const speak = useCallback((word: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(word.replace(/[.!?]/g, ''));
    u.rate = speed;
    window.speechSynthesis.speak(u);
  }, [speed]);

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <motion.button
          type="button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onBack}
          className="p-2 rounded-xl bg-cream/10 border border-cream/10 text-cream hover:bg-cream/15"
        >
          <ArrowLeft className="w-5 h-5" />
        </motion.button>
        <h2 className="text-2xl font-medium text-cream">Guided Reading</h2>
      </div>

      <p className="text-cream/70">Tap a word to hear it. Adjust speed below.</p>

      <div className="rounded-2xl bg-cream/5 border border-cream/10 p-8">
        <div className="flex flex-wrap gap-2 justify-center">
          {words.map((word, i) => (
            <motion.button
              key={i}
              type="button"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setHighlightIndex(i);
                speak(word);
              }}
              className={`px-4 py-2 rounded-xl border-2 transition-colors ${
                highlightIndex === i
                  ? 'border-clay bg-clay/20 text-cream'
                  : 'border-cream/10 bg-transparent text-cream/90 hover:bg-cream/10'
              }`}
            >
              {word}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-cream/60 text-sm">Speed</span>
        <input
          type="range"
          min="0.5"
          max="1.5"
          step="0.1"
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
          className="flex-1 h-2 rounded-full bg-cream/10 appearance-none accent-clay"
        />
        <span className="text-cream text-sm w-10">{speed.toFixed(1)}x</span>
      </div>
    </div>
  );
}
