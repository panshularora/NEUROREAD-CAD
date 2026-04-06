import { motion, AnimatePresence } from 'framer-motion';
import { useLearningStore } from '../../store/useLearningStore';

export default function FeedbackOverlay() {
  const feedback = useLearningStore((state) => state.feedbackPlan);

  if (!feedback) return null;

  return (
    <AnimatePresence>
      <motion.div 
        className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-transparent backdrop-blur-sm rounded-[2rem]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
           animate={feedback.visual_feedback === "wobble" ? { x: [-10, 10, -10, 10, 0] } : { scale: [1, 1.2, 1] }}
           transition={{ duration: 0.5 }}
           className={`w-32 h-32 flex items-center justify-center rounded-full ${feedback.is_correct ? 'bg-moss/20' : 'bg-clay/20'}`}
        >
          {feedback.is_correct ? (
             <span className="iconify text-moss w-20 h-20" data-icon="solar:star-fall-bold" />
          ) : (
             <span className="iconify text-clay w-20 h-20" data-icon="solar:danger-triangle-bold" />
          )}
        </motion.div>

        <h2 className="text-3xl font-opendyslexic text-cream font-bold mt-6 text-center px-4 drop-shadow-md">
          {feedback.spoken_feedback}
        </h2>

        {feedback.xp_animation !== "none" && (
           <motion.div 
             initial={{ y: 0, opacity: 1 }} 
             animate={{ y: -60, opacity: 0 }} 
             transition={{ duration: 1.5, delay: 0.2 }}
             className="text-4xl text-moss font-bold mt-4 drop-shadow-md"
           >
             {feedback.xp_animation}
           </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
