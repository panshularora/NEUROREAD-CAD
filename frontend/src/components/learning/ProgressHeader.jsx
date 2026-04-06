import { useLearningStore } from '../../store/useLearningStore';

export default function ProgressHeader() {
  const stats = useLearningStore((state) => state.stats);
  const flowState = useLearningStore((state) => state.flowState);
  const session = useLearningStore((state) => state.session);

  const maxExercises = session?.session_config?.max_exercises || 10;

  return (
    <div className="w-full flex justify-between items-center p-6 bg-transparent absolute top-0 left-0 z-40">
      <div className="flex gap-2">
        {Array.from({ length: maxExercises }).map((_, i) => (
          <div key={i} className={`w-3 h-3 rounded-full ${i < stats.completed ? 'bg-moss' : 'bg-moss/20'}`} />
        ))}
      </div>

      <div className="flex items-center gap-4">
         {flowState?.anxiety_signal > 0.5 && <span className="text-clay text-sm font-bold bg-white/10 px-2 py-1 rounded">Take your time! 🧘🏽‍♂️</span>}
         {flowState?.flow_score >= 0.9 && <span className="text-moss text-sm font-bold bg-white/10 px-2 py-1 rounded">You're on fire! 🔥</span>}
         
         <div className="bg-moss/20 px-4 py-2 rounded-full font-bold text-moss border border-moss/30 shadow-sm">
           {stats.xp} XP
         </div>
      </div>
    </div>
  );
}
