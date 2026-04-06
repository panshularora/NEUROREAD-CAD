import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { debounce } from 'lodash';
import { useMultimodalTTS } from '../../../hooks/useMultimodalTTS';

export default function TapReadingExercise({ data, onSubmit, colors, modality }) {
  const [startTime] = useState(Date.now());
  const { playTTS } = useMultimodalTTS(modality);
  const [options, setOptions] = useState([]);
  
  useEffect(() => {
    const opts = [data.correct_answer, ...(data.distractors || [])];
    setOptions(opts.sort(() => Math.random() - 0.5));
  }, [data]);

  const handleSelect = useCallback(debounce((opt) => {
    const timeMs = Date.now() - startTime;
    onSubmit(opt, timeMs);
  }, 500), [startTime, onSubmit]);

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-3xl font-opendyslexic">
      <button 
        onClick={playTTS}
        className="mb-6 w-16 h-16 rounded-full bg-cream/10 flex items-center justify-center hover:bg-cream/20"
      >
        <span className="iconify text-3xl text-cream" data-icon="solar:volume-loud-bold" />
      </button>

      {data.story_context && (
        <div className="bg-cream/10 p-8 rounded-3xl mb-10 w-full text-center shadow-inner">
          <p className="text-3xl text-cream leading-relaxed font-medium">
            {data.story_context}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 w-full px-4">
        {options.map((opt, idx) => (
          <motion.button
            key={idx}
            whileHover={{ scale: 1.02, x: 10 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleSelect(opt)}
            className="p-6 rounded-2xl text-2xl font-bold bg-cream text-charcoal shadow hover:bg-cream/90 flex items-center"
          >
            <div className="w-8 h-8 rounded-full bg-charcoal/10 mr-4 flex items-center justify-center text-sm">{idx + 1}</div>
            {opt}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
