import { create } from 'zustand';

export const useLearningStore = create((set) => ({
  session: null,
  flowState: null,
  currentExercise: null,
  isLoading: true,
  feedbackPlan: null,
  stats: { xp: 0, completed: 0, accuracy: 0 },
  
  setSession: (data) => set({ session: data }),
  setCurrentExercise: (exercise) => set({ currentExercise: exercise, isLoading: false, feedbackPlan: null }),
  setFeedback: (plan) => set({ feedbackPlan: plan }),
  setFlowState: (flow) => set({ flowState: flow }),
  updateStats: (newStats, xpGain) => set((state) => ({ 
      stats: { ...newStats, xp: state.stats.xp + xpGain } 
  })),
}));
