/**
 * Interactive Phonics: letter tap → sound playback, animated phoneme breakdown, waveform.
 */
import React, { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

const WAVE_BARS = 5;

interface ModulePhonicsProps {
  onBack: () => void;
  childId: string;
}

export default function ModulePhonics({ onBack, childId }: ModulePhonicsProps) {
  const [letters] = useState(() =>
    ['a', 'b', 'c', 'd', 'e'].map((letter) => ({
      letter,
      sound: `/${letter}/`,
    }))
  );
  const [playing, setPlaying] = useState<string | null>(null);

  const speak = useCallback((letter: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    setPlaying(letter);
    const u = new SpeechSynthesisUtterance(letter);
    u.rate = 0.9;
    u.onend = () => setPlaying(null);
    window.speechSynthesis.speak(u);
  }, []);

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
        <h2 className="text-2xl font-medium text-cream">Interactive Phonics</h2>
      </div>

      <p className="text-cream/70">Tap each letter to hear its sound.</p>

      <div className="flex flex-wrap gap-6 justify-center">
        {letters.map(({ letter, sound }, i) => (
          <motion.button
            key={letter}
            type="button"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => speak(letter)}
            className="w-20 h-20 rounded-2xl bg-clay/20 border-2 border-clay/40 flex flex-col items-center justify-center gap-1 hover:bg-clay/30"
          >
            <span className="text-3xl font-bold text-cream uppercase">{letter}</span>
            <span className="text-xs text-cream/60">{sound}</span>
            {playing === letter && (
              <div className="flex items-center gap-0.5 h-4">
                {Array.from({ length: WAVE_BARS }).map((_, j) => (
                  <motion.div
                    key={j}
                    className="w-1 bg-clay rounded-full"
                    animate={{ height: [6, 16, 6] }}
                    transition={{ duration: 0.4, repeat: Infinity, delay: j * 0.08 }}
                  />
                ))}
              </div>
            )}
          </motion.button>
        ))}
      </div>

      <div className="rounded-xl bg-cream/5 border border-cream/10 p-4">
        <p className="text-sm text-cream/60 mb-2">Phoneme breakdown (example)</p>
        <div className="flex flex-wrap gap-2">
          {letters.map(({ letter, sound }) => (
            <span
              key={letter}
              className="px-3 py-1.5 rounded-lg bg-cream/10 text-cream text-sm"
            >
              {letter} → {sound}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
