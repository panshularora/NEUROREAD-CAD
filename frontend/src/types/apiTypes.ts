// Request payload for /simplify
export interface SimplifyRequest {
  text: string;
  profile: UserProfile;
  user_id?: string;                 // optional (backend allows None)
  level?: number | null;            // optional
  enable_dyslexia_support?: boolean; 
  enable_audio?: boolean;
}
// Allowed reading profiles
export type UserProfile = 'default' | 'focus' | 'easy_read' | 'academic';

// Response from /simplify endpoint
export interface SimplifyResponse {
  auto_selected_level: number;
  profile_used: string;
  overload_warning: string | null;
  isolation_mode: boolean;
  original_analysis: any;
  simplified_text: string;
  dyslexia_optimized_text: string | null;
  audio_mode: any;
  simplified_analysis: any;
  cognitive_load_reduction: number;
  impact_summary: string;
  audio_file: string;

  // ✅ Frontend-derived (not from backend)
  cognitive_score?: number;
  reading_time?: number;
  difficulty?: string;
  reduction_percent?: number;
}
// Response from /progress/{user_id}
export interface ProgressResponse {
  total_sessions: number;
  average_cognitive_score: number;
  last_score: number;
  preferred_level: string;
}

// ---- Learning Mode APIs ----
export interface SessionStartResponse {
  session_id: string;
  child_id: string;
  learning_level: number;
  exercise: LearningExercise;
  started_at: string;
}

export type LearningExercise =
  | { type: 'phonics'; exercise_id: string; task: string; letters: { letter: string; sound: string }[]; instruction: string }
  | { type: 'spelling'; exercise_id: string; word: string; scrambled: string; instruction: string }
  | { type: 'comprehension'; exercise_id: string; question: string; options: string[]; correct_index: number; instruction: string }
  | { type: 'reading'; exercise_id: string; sentence: string; instruction: string }
  | { type: 'complete'; message: string };

export interface SubmitResponsePayload {
  session_id: string;
  exercise_id: string;
  is_correct: boolean;
  response?: string | number | string[] | null;
  expected?: string | null;
  actual?: string | null;
}

export interface SubmitResponseResult {
  correct: boolean;
  xp_delta: number;
  message: string;
  next_exercise: LearningExercise | null;
  session_ended: boolean;
  recommendations?: { id: string; type: string; message: string; priority: number }[] | null;
}

export interface LearningProgressResponse {
  child_id: string;
  age: number;
  learning_level: number;
  total_xp: number;
  streak_days: number;
  error_patterns: Record<string, number>;
  progress_metrics: Record<string, number>;
  recommendations: { id: string; type: string; message: string; priority: number }[];
}

