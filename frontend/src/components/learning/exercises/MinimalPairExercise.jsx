import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { debounce } from 'lodash';
import { useMultimodalTTS } from '../../../hooks/useMultimodalTTS';
import { ColoredPhonemeText } from './ColoredPhonemeText';

export default function MinimalPairExercise({ data, onSubmit, colors, modality }) {
  const [startTime] = useState(Date.now());
  const { playTTS } = useMultimodalTTS(modality);
  const [selected, setSelected] = useState(null);

  // Combine correct answer and distractors, then shuffle
  const [options, setOptions] = useState([]);
  
  useEffect(() => {
    const opts = [data.correct_answer, ...(data.distractors || [])];
    setOptions(opts.sort(() => Math.random() - 0.5));
  }, [data]);

  const handleSelect = useCallback(debounce((opt) => {
    setSelected(opt);
    const timeMs = Date.now() - startTime;
    onSubmit(opt, timeMs);
  }, 500, { leading: true, trailing: false }), [startTime, onSubmit]);

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-3xl font-opendyslexic">
      <button 
        onClick={playTTS}
        className="mb-8 w-20 h-20 rounded-full bg-cream/10 flex items-center justify-center hover:bg-cream/20 transition-colors shadow-sm"
      >
        <span className="iconify text-4xl text-cream" data-icon="solar:volume-loud-bold" />
      </button>

      {modality.stimulus_format.includes('text') && data.target_word && (
        <div className="text-5xl font-bold text-cream mb-12">
          <ColoredPhonemeText text={data.target_word} colorMap={colors} />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full px-4">
        {options.map((opt, idx) => (
          <motion.button
            key={idx}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSelect(opt)}
            className={`p-8 rounded-3xl text-4xl font-bold shadow-lg flex items-center justify-center transition-all ${
              selected === opt ? 'bg-moss/80 text-cream' : 'bg-cream text-charcoal hover:bg-cream/90'
            }`}
          >
            <ColoredPhonemeText text={opt} colorMap={colors} />
          </motion.button>
        ))}
      </div>
    </div>
  );
}
