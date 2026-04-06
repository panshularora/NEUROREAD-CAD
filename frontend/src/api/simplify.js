const API_URL = 'http://127.0.0.1:8000/assistive/simplify';

function mapProfile(profile) {
  const p = (profile || '').toLowerCase();
  if (p.includes('dyslexia')) return 'easy_read';
  if (p.includes('adhd')) return 'focus';
  if (p.includes('technical') || p.includes('expert') || p.includes('academic')) return 'academic';
  return 'default';
}

function difficultyFromScore(score) {
  if (score >= 70) return 'High';
  if (score >= 40) return 'Moderate';
  return 'Low';
}

function minutesLabel(minutes) {
  const m = Number(minutes);
  if (!Number.isFinite(m)) return '—';
  const rounded = Math.max(1, Math.round(m));
  return `${rounded} min`;
}

function adaptResponse(data) {
  // FastAPI backend shape (backend/app/routes/assistive/simplify.py)
  if (data && typeof data === 'object' && 'simplified_text' in data) {
    const originalScore = Math.round(data.original_analysis?.cognitive_load_score ?? 0);
    const simplifiedScore = Math.round(data.simplified_analysis?.cognitive_load_score ?? 0);
    const reductionPoints = Number(data.cognitive_load_reduction ?? 0);
    const reductionPct =
      originalScore > 0 ? Math.max(0, Math.round((reductionPoints / originalScore) * 100)) : 0;

    return {
      simplifiedText: data.simplified_text ?? '',
      originalScore: originalScore || 0,
      readingTime: minutesLabel(data.original_analysis?.estimated_reading_time_minutes),
      difficulty: difficultyFromScore(originalScore),
      reduction: reductionPct,
      intensity: simplifiedScore || 0,
      impactSummary: data.impact_summary ?? '',
      keywords: Array.isArray(data.keywords) ? data.keywords : [],
    };
  }

  // Flask mock shape
  return data;
}

export async function simplifyText(text, profile) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, profile: mapProfile(profile) }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`Simplify request failed (${res.status}): ${detail || res.statusText}`);
  }

  const data = await res.json();
  return adaptResponse(data);
}

