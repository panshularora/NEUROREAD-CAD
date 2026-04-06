import { useEffect, useMemo, useRef } from 'react';

export default function SimplifierModal({
  open,
  onClose,
  userId,
  onUserIdChange,
  profile,
  onProfileChange,
  inputText,
  onInputTextChange,
  dyslexiaOn,
  onToggleDyslexia,
  audioOn,
  onToggleAudio,
  simplifiedText,
  loading,
  metrics,
  error,
  onRunSimplifier,
}) {
  const overlayRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') onRunSimplifier();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, onClose, onRunSimplifier]);

  useEffect(() => {
    if (open) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    window.Iconify?.scan?.();
  }, [open, simplifiedText, metrics]);

  const dyslexiaStyle = useMemo(() => {
    if (!dyslexiaOn) return undefined;
    return { letterSpacing: '.06em', lineHeight: '2.2', wordSpacing: '.18em' };
  }, [dyslexiaOn]);

  if (!open) return null;

  const scoreBadgeClass = (() => {
    const diff = (metrics?.difficulty || 'PENDING').toLowerCase();
    const bc = {
      high: 'bg-red-50 text-red-600 border-red-200',
      moderate: 'bg-clay/10 text-clay border-clay/20',
      low: 'bg-moss/10 text-moss border-moss/20',
      pending: 'bg-charcoal/8 text-charcoal/50 border border-charcoal/10',
    };
    const base = 'text-xs font-medium px-3 py-1 rounded-full border';
    return `${base} ${bc[diff] || bc.moderate}`;
  })();

  return (
    <div
      id="simplifier-modal"
      ref={overlayRef}
      className="flex"
      onMouseDown={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      <div className="modal-box">
        <div className="flex items-center justify-between px-8 pt-7 pb-5 border-b border-moss/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-moss flex items-center justify-center">
              <span
                className="iconify text-cream"
                data-icon="solar:magic-stick-3-linear"
                style={{ width: '1.1rem', height: '1.1rem' }}
              />
            </div>
            <div>
              <h2 className="font-medium text-lg text-charcoal leading-none">Smart Simplifier</h2>
              <p className="text-xs text-charcoal/50 mt-0.5">AI-powered cognitive load reduction</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-moss/8 hover:bg-moss/15 flex items-center justify-center transition-colors border border-moss/10"
            aria-label="Close simplifier"
          >
            <span className="iconify text-charcoal/60" data-icon="solar:close-linear" style={{ width: '1.1rem', height: '1.1rem' }} />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-0">
          <div className="lg:col-span-3 p-6 md:p-8 border-r border-moss/10">
            <h3 className="font-medium text-base text-charcoal mb-1">Text Simplifier</h3>
            <p className="text-xs text-charcoal/50 mb-5">
              Paste or type text to analyse and simplify according to your reading profile.
            </p>

            <div className="grid grid-cols-2 gap-3 mb-2">
              <div>
                <label className="text-[10px] font-medium text-charcoal/50 uppercase tracking-wider block mb-1.5">
                  User ID
                </label>
                <input
                  value={userId}
                  onChange={(e) => onUserIdChange(e.target.value)}
                  type="text"
                  className="w-full rounded-xl border border-moss/15 bg-white px-4 py-2.5 text-sm text-charcoal focus:outline-none focus:ring-2 focus:ring-moss/20"
                />
              </div>
              <div>
                <label className="text-[10px] font-medium text-charcoal/50 uppercase tracking-wider block mb-1.5">
                  Reading Profile
                </label>
                <select
                  value={profile}
                  onChange={(e) => onProfileChange(e.target.value)}
                  className="w-full rounded-xl border border-moss/15 bg-white px-4 py-2.5 text-sm text-charcoal focus:outline-none focus:ring-2 focus:ring-moss/20 appearance-none"
                >
                  <option>Default</option>
                  <option>Dyslexia Support</option>
                  <option>ADHD Mode</option>
                  <option>Technical Expert</option>
                </select>
              </div>
            </div>
            <p className="text-[11px] text-charcoal/40 mb-5">Used to fetch your long-term cognitive progress.</p>

            <label className="text-[10px] font-medium text-charcoal/50 uppercase tracking-wider block mb-1.5">
              Text to Simplify
            </label>
            <textarea
              value={inputText}
              onChange={(e) => onInputTextChange(e.target.value)}
              rows={9}
              placeholder={'Paste or type text that may be cognitively demanding...\nPress Ctrl/⌘ + Enter to simplify.'}
              className="w-full rounded-xl border border-moss/15 bg-white px-4 py-3 text-sm text-charcoal focus:outline-none focus:ring-2 focus:ring-moss/20 placeholder-charcoal/30 resize-y leading-relaxed"
            />

            <div className="flex items-center justify-between mt-4 flex-wrap gap-3">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onToggleDyslexia}
                  className={`px-4 py-2 rounded-full border border-moss/20 text-xs font-medium text-charcoal hover:bg-moss hover:text-cream transition-all ${
                    dyslexiaOn ? 'bg-moss text-cream' : ''
                  }`}
                >
                  Dyslexia mode
                </button>
                <button
                  type="button"
                  onClick={onToggleAudio}
                  className={`px-4 py-2 rounded-full border border-moss/20 text-xs font-medium text-charcoal hover:bg-moss hover:text-cream transition-all flex items-center gap-2 ${
                    audioOn ? 'bg-moss text-cream' : ''
                  }`}
                >
                  <div className={`wave-bars ${audioOn ? 'playing' : ''}`}>
                    <div className="wave-bar bar1" />
                    <div className="wave-bar bar2" />
                    <div className="wave-bar bar3" />
                    <div className="wave-bar bar4" />
                    <div className="wave-bar bar5" />
                  </div>
                  Audio mode
                </button>
              </div>

              <button
                type="button"
                onClick={onRunSimplifier}
                disabled={loading}
                className="magnetic-btn px-6 py-2.5 rounded-full bg-clay text-cream text-xs font-medium uppercase tracking-wide disabled:opacity-70"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-3 h-3 border-2 border-cream border-t-transparent rounded-full animate-spin" />
                    Analysing...
                  </span>
                ) : (
                  <span>Simplify text</span>
                )}
              </button>
            </div>

            <div className="mt-6 border border-moss/10 rounded-2xl overflow-hidden">
              <div className="flex items-center justify-between px-5 py-3 bg-white border-b border-moss/8">
                <h4 className="text-xs font-medium text-charcoal uppercase tracking-wider">Adapted Reading View</h4>
                <button
                  type="button"
                  onClick={onToggleDyslexia}
                  className={`text-[10px] px-3 py-1 rounded-full bg-moss/8 text-moss font-medium hover:bg-moss hover:text-cream transition-all ${
                    dyslexiaOn ? 'bg-moss text-cream' : ''
                  }`}
                >
                  Dyslexia Mode
                </button>
              </div>
              <div className="px-5 py-4 bg-white">
                <p className="text-[10px] font-medium text-charcoal/40 uppercase tracking-wider mb-3">Simplified Content</p>
                <div
                  className="min-h-[80px] rounded-xl bg-moss/6 border border-moss/10 px-5 py-4 text-sm text-charcoal/70 leading-relaxed italic whitespace-pre-wrap"
                  style={dyslexiaStyle}
                >
                  {loading ? (
                    <div>
                      <div className="shimmer w-full" />
                      <div className="shimmer w-4/5" />
                      <div className="shimmer w-3/5" />
                    </div>
                  ) : error ? (
                    error
                  ) : (
                    simplifiedText || 'Simplified text will appear here once you run an analysis.'
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 p-6 md:p-8 bg-moss/[0.03]">
            <h3 className="font-medium text-base text-charcoal mb-1">Cognitive Load Overview</h3>
            <div className="w-12 h-px bg-moss/20 mb-5" />

            <div className="rounded-2xl bg-white border border-moss/10 p-5 mb-4">
              <p className="text-[10px] font-medium text-charcoal/40 uppercase tracking-wider mb-3">Cognitive Score</p>
              <div className="flex items-center justify-between">
                <div className={scoreBadgeClass}>{(metrics?.difficulty || 'PENDING').toUpperCase?.() || 'PENDING'}</div>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-medium text-charcoal">{metrics?.originalScore ?? '—'}</span>
                  <span className="text-sm text-charcoal/40">/ 100</span>
                </div>
              </div>
              <div className="mt-3 h-1.5 rounded-full bg-moss/10 overflow-hidden">
                <div
                  className="h-full rounded-full bg-moss transition-all duration-1000"
                  style={{ width: `${metrics?.originalScore ?? 0}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
              <div className="rounded-2xl bg-clay/8 border border-clay/15 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="iconify text-charcoal/60" data-icon="solar:clock-circle-linear" style={{ width: '1rem', height: '1rem' }} />
                  <span className="text-[10px] font-medium text-charcoal/50 uppercase tracking-wider">Reading Time</span>
                </div>
                <p className="text-xl font-medium text-charcoal mt-1">{metrics?.readingTime ?? '—'}</p>
                <div className="w-6 h-0.5 bg-charcoal/20 mt-2 rounded-full" />
              </div>
              <div className="rounded-2xl bg-clay/8 border border-clay/15 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="iconify text-charcoal/60" data-icon="solar:graph-linear" style={{ width: '1rem', height: '1rem' }} />
                  <span className="text-[10px] font-medium text-charcoal/50 uppercase tracking-wider">Difficulty</span>
                </div>
                <p className="text-xl font-medium text-charcoal mt-1">{metrics?.difficulty ?? '—'}</p>
                <div className="w-6 h-0.5 bg-charcoal/20 mt-2 rounded-full" />
              </div>
            </div>

            <div className="rounded-2xl bg-clay/8 border border-clay/15 p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="iconify text-charcoal/60" data-icon="solar:bolt-linear" style={{ width: '1rem', height: '1rem' }} />
                <span className="text-[10px] font-medium text-charcoal/50 uppercase tracking-wider">Reduction</span>
              </div>
              <p className="text-xl font-medium text-charcoal mt-1">{metrics?.reduction != null ? `${metrics.reduction}%` : '—'}</p>
              <div className="w-6 h-0.5 bg-charcoal/20 mt-2 rounded-full" />
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[11px] text-moss font-medium">Cognitive Load Intensity</p>
                <span className="text-[11px] text-charcoal/40">{metrics?.intensity != null ? `${metrics.intensity} / 100` : '—'}</span>
              </div>
              <div className="h-2 rounded-full bg-moss/10 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-moss/60 to-clay transition-all duration-1000"
                  style={{ width: `${metrics?.intensity ?? 0}%` }}
                />
              </div>
            </div>

            <div className="rounded-2xl bg-white border border-moss/10 p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="iconify text-moss" data-icon="solar:lightbulb-linear" style={{ width: '1.1rem', height: '1.1rem' }} />
                <h4 className="text-sm font-medium text-charcoal">Impact Summary</h4>
              </div>
              <p className="text-xs text-charcoal/60 leading-relaxed">
                {metrics?.impactSummary ||
                  'Run a simplification to see the cognitive impact analysis and personalised recommendations.'}
              </p>
            </div>

            {metrics?.keywords?.length ? (
              <div className="mt-4">
                <p className="text-[10px] font-medium text-charcoal/40 uppercase tracking-wider mb-2">Key Terms Detected</p>
                <div className="flex flex-wrap gap-2">
                  {metrics.keywords.map((k) => (
                    <span
                      key={k}
                      className="text-[11px] px-3 py-1 rounded-full bg-moss/8 text-moss border border-moss/15 font-medium"
                    >
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

