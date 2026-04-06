import { useEffect, useState, useCallback } from 'react';
import { useLearningStore } from '../../store/useLearningStore';
import ExerciseRenderer from './ExerciseRenderer';
import FeedbackOverlay from './FeedbackOverlay';
import SessionCelebration from './SessionCelebration';
import ProgressHeader from './ProgressHeader';
import * as api from '../../api/learningApi';

export default function LearningEngine({ childProfile }) {
  const { session, currentExercise, setSession, setCurrentExercise, setFeedback, updateStats, setFlowState } = useLearningStore();
  const [sessionEnded, setSessionEnded] = useState(false);
  const [endReason, setEndReason] = useState(null);
  const [error, setError] = useState(null);

  // 1. Start continuous session
  useEffect(() => {
    const initSession = async () => {
      try {
        setError(null);
        const data = await api.startSession(childProfile);
        console.log("Session started:", data);
        setSession(data);
        setCurrentExercise(data.first_exercise);
        setFlowState(data.flow_state);
      } catch (err) {
        console.error("Failed to start session", err);
        setError(err.message);
      }
    };
    initSession();
  }, [JSON.stringify(childProfile), setSession, setCurrentExercise, setFlowState]);

  // 2. Continuous submission loop
  const handleSubmission = useCallback(async (answer, timeMs) => {
    if (!session) return;
    try {
      const response = await api.submitAnswer(session.session_id, answer, timeMs);
      
      setFeedback(response.feedback);
      updateStats({ completed: response.session_stats.completed, accuracy: response.session_stats.accuracy }, response.xp_earned);
      setFlowState(response.flow_state);

      if (response.session_should_end) {
        setEndReason(response.end_reason);
        setTimeout(() => setSessionEnded(true), 2500); 
      } else {
        setTimeout(() => setCurrentExercise(response.next_exercise), 2500);
      }
    } catch (err) {
      console.error("Failed to submit", err);
    }
  }, [session, setFeedback, updateStats, setFlowState, setCurrentExercise]);

  if (error) return <div className="text-red-400 text-center mt-20">Error: {error}</div>;
  if (!currentExercise && !sessionEnded) return <div className="text-cream text-center mt-20">Loading AI Tutor...</div>;
  if (sessionEnded) return <SessionCelebration sessionId={session?.session_id} endReason={endReason} />;

  return (
    <div className="learning-engine-container relative h-full min-h-[400px] w-full bg-transparent flex flex-col items-center justify-center">
      <ProgressHeader />
      <FeedbackOverlay />
      
      {!useLearningStore.getState().feedbackPlan && (
        <ExerciseRenderer 
          exercise={currentExercise} 
          onSubmit={handleSubmission} 
          config={session?.session_config} 
        />
      )}
    </div>
  );
}
