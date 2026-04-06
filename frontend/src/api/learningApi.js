const BASE_URL = 'http://localhost:8000';

export async function startSession(childProfile) {
  const response = await fetch(`${BASE_URL}/learning/session/start_flow`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(childProfile),
  });
  if (!response.ok) throw new Error('Failed to start session');
  return response.json();
}

export async function submitAnswer(sessionId, answer, timeMs) {
  const response = await fetch(`${BASE_URL}/learning/response/submit_flow`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, answer, response_time_ms: timeMs }),
  });
  if (!response.ok) throw new Error('Failed to submit answer');
  return response.json();
}
