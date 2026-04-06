import axios from 'axios';
import type {
  SimplifyRequest,
  SimplifyResponse,
  ProgressResponse,
  SessionStartResponse,
  LearningExercise,
  SubmitResponsePayload,
  SubmitResponseResult,
  LearningProgressResponse,
} from '../types/apiTypes';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 15000,
});

export const postSimplify = async (payload: SimplifyRequest): Promise<SimplifyResponse> => {
  const { data } = await apiClient.post<SimplifyResponse>('/simplify', payload);
  return data;
};

export const getProgress = async (userId: string): Promise<ProgressResponse> => {
  const { data } = await apiClient.get<ProgressResponse>(`/progress/${encodeURIComponent(userId)}`);
  return data;
};

// ---- Learning Mode ----
export const sessionStart = async (childId: string, age: number = 6): Promise<SessionStartResponse> => {
  const { data } = await apiClient.post<SessionStartResponse>('/session/start', { child_id: childId, age });
  return data;
};

export const exerciseNext = async (sessionId: string): Promise<{ exercise: LearningExercise }> => {
  const { data } = await apiClient.get<{ exercise: LearningExercise }>('/exercise/next', {
    params: { session_id: sessionId },
  });
  return data;
};

export const responseSubmit = async (payload: SubmitResponsePayload): Promise<SubmitResponseResult> => {
  const { data } = await apiClient.post<SubmitResponseResult>('/response/submit', payload);
  return data;
};

export const getLearningProgress = async (childId: string): Promise<LearningProgressResponse> => {
  const { data } = await apiClient.get<LearningProgressResponse>('/progress', {
    params: { child_id: childId },
  });
  return data;
};

export const getRecommendations = async (childId: string): Promise<{ recommendations: LearningProgressResponse['recommendations'] }> => {
  const { data } = await apiClient.get('/recommendations', { params: { child_id: childId } });
  return data;
};

