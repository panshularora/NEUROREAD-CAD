import { AnimatePresence, motion } from 'framer-motion';
import ConstructionExercise from './exercises/ConstructionExercise';
import MinimalPairExercise from './exercises/MinimalPairExercise';
import TapReadingExercise from './exercises/TapReadingExercise';

export default function ExerciseRenderer({ exercise, onSubmit, config }) {
  if (!exercise || !exercise.exercise_type) return null;

  const ComponentMap = {
    "WORD_CONSTRUCTION": ConstructionExercise,
    "CONFUSABLE_SORT": ConstructionExercise, 
    "MINIMAL_PAIR_CHOICE": MinimalPairExercise,
    "PHONEME_ISOLATION": MinimalPairExercise, 
    "STORY_COMPREHENSION": TapReadingExercise,
    "LETTER_SOUND_MATCH": MinimalPairExercise,
    "RHYME_DETECTION": MinimalPairExercise,
    "WORD_IN_CONTEXT": MinimalPairExercise
  };

  const ActiveExercise = ComponentMap[exercise.exercise_type] || MinimalPairExercise;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={exercise.correct_answer + Math.random()} 
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: -20 }}
        transition={{ duration: 0.4 }}
        className="w-full h-full flex flex-col items-center justify-center"
      >
        <ActiveExercise 
           data={exercise} 
           onSubmit={onSubmit} 
           colors={config?.letter_colors || {}} 
           modality={exercise.modality_plan}
        />
      </motion.div>
    </AnimatePresence>
  );
}
