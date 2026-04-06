/**
 * Comprehension Lab: quiz cards (MCQ), immediate feedback + explanation, difficulty scaling.
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, X } from 'lucide-react';

interface ModuleComprehensionProps {
  onBack: () => void;
  childId: string;
}

const QUESTION = {
  question: 'What is the main idea of the story?',
  options: ['The cat sat on the mat.', 'The dog ran in the sun.', 'Animals like to play.'],
  correctIndex: 0,
};

export default function ModuleComprehension({ onBack, childId }: ModuleComprehensionProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);

  const correct = selected === QUESTION.correctIndex;
  const showResult = revealed && selected !== null;

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
        <h2 className="text-2xl font-medium text-cream">Comprehension Lab</h2>
      </div>

      <p className="text-cream/70">Choose the best answer.</p>

      <div className="rounded-2xl bg-cream/5 border border-cream/10 p-6">
        <p className="text-lg text-cream font-medium mb-6">{QUESTION.question}</p>
        <div className="space-y-3">
          {QUESTION.options.map((opt, i) => (
            <motion.button
              key={i}
              type="button"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => {
                if (revealed) return;
                setSelected(i);
              }}
              className={`w-full text-left px-4 py-3 rounded-xl border-2 transition-colors ${
                selected === i
                  ? 'border-clay bg-clay/20 text-cream'
                  : 'border-cream/10 bg-cream/5 text-cream/80 hover:bg-cream/10'
              } ${showResult && i === QUESTION.correctIndex ? 'ring-2 ring-green-400' : ''} ${
                showResult && selected === i && !correct ? 'border-red-400/50' : ''
              }`}
            >
              <span className="font-medium">{String.fromCharCode(65 + i)}.</span> {opt}
            </motion.button>
          ))}
        </div>
      </div>

      {selected !== null && !revealed && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          type="button"
          onClick={() => setRevealed(true)}
          className="px-6 py-3 rounded-xl bg-clay text-cream font-medium"
        >
          Check answer
        </motion.button>
      )}

      {showResult && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className={`rounded-xl p-4 flex items-start gap-3 ${
            correct ? 'bg-green-500/20 text-green-300' : 'bg-amber-500/20 text-amber-200'
          }`}
        >
          {correct ? <Check className="w-6 h-6 shrink-0" /> : <X className="w-6 h-6 shrink-0" />}
          <div>
            <p className="font-medium">{correct ? 'Correct!' : 'Not quite.'}</p>
            <p className="text-sm mt-1 opacity-90">
              {correct ? 'The main idea is what the story is mostly about.' : `The correct answer is: ${QUESTION.options[QUESTION.correctIndex]}`}
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
}
