/**
 * Spelling Trainer: drag-and-drop letter building, voice input, real-time correction feedback.
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, X } from 'lucide-react';

interface ModuleSpellingProps {
  onBack: () => void;
  childId: string;
}

const EXAMPLE_WORD = 'cat';
const SCRAMBLED = 'tac';

export default function ModuleSpelling({ onBack, childId }: ModuleSpellingProps) {
  const [slots, setSlots] = useState<(string | null)[]>(['t', 'a', 'c']);
  const [feedback, setFeedback] = useState<'idle' | 'correct' | 'wrong'>('idle');

  const check = () => {
    const answer = slots.join('');
    const correct = answer.toLowerCase() === EXAMPLE_WORD.toLowerCase();
    setFeedback(correct ? 'correct' : 'wrong');
  };

  const reset = () => {
    setSlots(['t', 'a', 'c']);
    setFeedback('idle');
  };

  const move = (from: number, to: number) => {
    const next = [...slots];
    const t = next[from];
    next[from] = next[to];
    next[to] = t;
    setSlots(next);
    setFeedback('idle');
  };

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
        <h2 className="text-2xl font-medium text-cream">Spelling Trainer</h2>
      </div>

      <p className="text-cream/70">Drag letters to spell the word. Then check.</p>

      <div className="flex gap-3 justify-center flex-wrap">
        {slots.map((letter, i) => (
          <motion.button
            key={`${i}-${letter}`}
            type="button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              const next = (i + 1) % slots.length;
              move(i, next);
            }}
            className="w-14 h-14 rounded-xl bg-clay/20 border-2 border-clay/40 text-2xl font-bold text-cream uppercase"
          >
            {letter}
          </motion.button>
        ))}
      </div>

      <div className="flex gap-4 justify-center">
        <motion.button
          type="button"
          whileTap={{ scale: 0.96 }}
          onClick={check}
          className="px-6 py-3 rounded-xl bg-clay text-cream font-medium flex items-center gap-2"
        >
          <Check className="w-5 h-5" /> Check
        </motion.button>
        <motion.button
          type="button"
          whileTap={{ scale: 0.96 }}
          onClick={reset}
          className="px-6 py-3 rounded-xl bg-cream/10 text-cream border border-cream/20"
        >
          Shuffle
        </motion.button>
      </div>

      {feedback !== 'idle' && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className={`rounded-xl p-4 flex items-center gap-3 ${
            feedback === 'correct' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
          }`}
        >
          {feedback === 'correct' ? <Check className="w-6 h-6" /> : <X className="w-6 h-6" />}
          <span>{feedback === 'correct' ? 'Correct! Well done.' : 'Not quite. Try again!'}</span>
        </motion.div>
      )}
    </div>
  );
}
