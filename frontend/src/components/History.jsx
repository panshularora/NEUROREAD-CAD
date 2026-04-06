export const DEFAULT_HISTORY = [
  {
    id: 'session-1',
    title: 'Session 1',
    date: 'Feb 27',
    originalScore: 78,
    simplifiedScore: 42,
    reduction: 46,
    difficultyFrom: 'High',
    difficultyTo: 'Moderate',
    summary:
      'Medical report analysis. High-density terminology reduced significantly. Reading time cut from 8 min to 4.5 min. Profile: Dyslexia Support.',
    accent: 'moss',
    isNew: false,
  },
  {
    id: 'session-2',
    title: 'Session 2',
    date: 'Feb 26',
    originalScore: 65,
    simplifiedScore: 35,
    reduction: 46,
    difficultyFrom: 'Moderate',
    difficultyTo: 'Low',
    summary:
      'Legal contract clause review. Dense passive voice and legal jargon replaced with plain language. Profile: Default.',
    accent: 'moss',
    isNew: false,
  },
  {
    id: 'session-3',
    title: 'Session 3',
    date: 'Feb 28',
    originalScore: 82,
    simplifiedScore: 46,
    reduction: 44,
    difficultyFrom: 'High',
    difficultyTo: 'Moderate',
    summary:
      'Academic research paper on neuroscience. Highest original complexity score. Multi-layered sentence structures broken into digestible points. Profile: Default.',
    accent: 'clay',
    isNew: false,
  },
  {
    id: 'session-4',
    title: 'Session 4',
    date: 'Feb 28',
    originalScore: 74,
    simplifiedScore: 39,
    reduction: 47,
    difficultyFrom: 'High',
    difficultyTo: 'Moderate',
    summary: 'Insurance policy fine print simplification. Profile: Dyslexia Support.',
    accent: 'moss',
    isNew: false,
  },
  {
    id: 'session-5',
    title: 'Session 5',
    date: 'Feb 28',
    originalScore: 69,
    simplifiedScore: 34,
    reduction: 51,
    difficultyFrom: 'Moderate',
    difficultyTo: 'Low',
    summary: 'Tech manual for software configuration. Largest reduction achieved. Profile: ADHD Mode.',
    accent: 'moss',
    isNew: false,
  },
  {
    id: 'session-6',
    title: 'Session 6',
    date: 'Feb 28',
    originalScore: 71,
    simplifiedScore: 37,
    reduction: 48,
    difficultyFrom: 'Moderate',
    difficultyTo: 'Low',
    summary: 'Pharmaceutical drug information leaflet. Dosage and side-effect language clarified. Profile: Default.',
    accent: 'moss',
    isNew: false,
  },
  {
    id: 'session-7',
    title: 'Session 7',
    date: 'Feb 28',
    originalScore: 76,
    simplifiedScore: 41,
    reduction: 46,
    difficultyFrom: 'High',
    difficultyTo: 'Moderate',
    summary:
      'Government policy document on housing regulations. Long compound sentences broken into bullet-style clarity. Profile: Default.',
    accent: 'moss',
    isNew: false,
  },
];

function Bar({ heightPct, label, colorClass, title }) {
  return (
    <div className="flex-1 flex flex-col items-center gap-1">
      <div
        className={`w-full rounded-t ${colorClass} hover:opacity-90 transition-colors cursor-default`}
        style={{ height: `${heightPct}%` }}
        title={title}
      />
      <span className="text-[9px] text-charcoal/40">{label}</span>
    </div>
  );
}

export default function History({ sessions = DEFAULT_HISTORY, expandedId, onToggleExpanded }) {
  return (
    <section id="history" className="py-24 bg-cream relative z-20 border-t border-moss/8">
      <div className="max-w-5xl mx-auto px-6">
        <div className="flex items-start justify-between mb-12 flex-wrap gap-4">
          <div>
            <span className="font-mono text-xs text-moss uppercase tracking-wider block mb-3">Your Progress</span>
            <h2 className="md:text-5xl text-charcoal text-4xl font-medium tracking-tight">Session History</h2>
            <p className="text-charcoal/50 text-sm mt-2">Past simplification sessions and cognitive improvement over time.</p>
          </div>
          <div className="flex items-center gap-3 flex-wrap mt-2">
            <div className="flex items-center gap-2 bg-white border border-moss/10 rounded-full px-4 py-2 text-xs">
              <span className="w-2 h-2 rounded-full bg-moss" />
              <span className="text-charcoal/60">{sessions.length} sessions</span>
            </div>
            <div className="flex items-center gap-2 bg-white border border-moss/10 rounded-full px-4 py-2 text-xs">
              <span className="w-2 h-2 rounded-full bg-clay" />
              <span className="text-charcoal/60">Avg reduction 45%</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-moss/10 rounded-[2rem] p-6 mb-8">
          <p className="text-[10px] font-medium text-charcoal/40 uppercase tracking-wider mb-4">
            Cognitive Score Over Time (Original → Simplified)
          </p>
          <div className="flex items-end gap-2 h-20">
            <Bar heightPct={78} label="Feb 27" colorClass="bg-moss/25 hover:bg-moss/50" title="Session 1: 78→42" />
            <Bar heightPct={65} label="Feb 26" colorClass="bg-moss/25 hover:bg-moss/50" title="Session 2: 65→35" />
            <Bar heightPct={82} label="Feb 28" colorClass="bg-clay/50 hover:bg-clay/70" title="Session 3: 82→46" />
            <Bar heightPct={74} label="Feb 28" colorClass="bg-moss/25 hover:bg-moss/50" title="Session 4: 74→39" />
            <Bar heightPct={69} label="Feb 28" colorClass="bg-moss/25 hover:bg-moss/50" title="Session 5: 69→34" />
            <Bar heightPct={71} label="Feb 28" colorClass="bg-moss/25 hover:bg-moss/50" title="Session 6: 71→37" />
            <Bar heightPct={76} label="Feb 28" colorClass="bg-moss/35 hover:bg-moss/60" title="Session 7: 76→41" />
          </div>
        </div>

        <div className="space-y-3" id="history-list">
          {sessions.map((s) => {
            const isOpen = expandedId === s.id;
            const accentBg = s.accent === 'clay' ? 'bg-clay/10' : 'bg-moss/8';
            const accentText = s.accent === 'clay' ? 'text-clay' : 'text-moss';
            const hoverBg = s.accent === 'clay' ? 'hover:bg-clay/[0.03]' : 'hover:bg-moss/[0.03]';
            const border = s.accent === 'clay' ? 'border-clay/25' : 'border-moss/10';

            return (
              <div
                key={s.id}
                className={`history-row rounded-[1.25rem] overflow-hidden border ${border} bg-white ${isOpen ? 'expanded' : ''}`}
              >
                <button
                  type="button"
                  onClick={() => onToggleExpanded(isOpen ? null : s.id)}
                  className={`w-full flex items-center justify-between px-6 py-4 text-left ${hoverBg} transition-colors`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-8 h-8 rounded-full ${accentBg} flex items-center justify-center`}>
                      <span
                        className={`iconify ${accentText}`}
                        data-icon="solar:document-text-linear"
                        style={{ width: '.9rem', height: '.9rem' }}
                      />
                    </div>
                    <div>
                      <span className="font-medium text-sm text-charcoal">{s.title}</span>
                      <span className="text-xs text-charcoal/40 ml-2">{s.date}</span>
                      {s.isNew ? <span className="text-xs text-clay font-medium ml-2">● New</span> : null}
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <span className="text-xs text-charcoal/60 hidden sm:block">
                      Score: <strong className="text-charcoal">{s.originalScore} → {s.simplifiedScore}</strong>
                    </span>
                    <span className="text-xs text-charcoal/60 hidden sm:block">
                      Difficulty: <strong className="text-charcoal">{s.difficultyFrom} → {s.difficultyTo}</strong>
                    </span>
                    <span
                      className="iconify history-chevron text-charcoal/40"
                      data-icon="solar:alt-arrow-down-linear"
                      style={{ width: '1rem', height: '1rem' }}
                    />
                  </div>
                </button>

                <div className={`history-row-body ${isOpen ? 'open' : ''}`}>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="bg-moss/5 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-charcoal/40 uppercase tracking-wider mb-1">Orig. Score</p>
                      <p className="text-lg font-medium text-charcoal">{s.originalScore}</p>
                    </div>
                    <div className="bg-clay/8 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-charcoal/40 uppercase tracking-wider mb-1">Simplified</p>
                      <p className="text-lg font-medium text-clay">{s.simplifiedScore}</p>
                    </div>
                    <div className="bg-moss/5 rounded-xl p-3 text-center">
                      <p className="text-[10px] text-charcoal/40 uppercase tracking-wider mb-1">Reduction</p>
                      <p className="text-lg font-medium text-moss">{s.reduction}%</p>
                    </div>
                  </div>
                  <p className="text-xs text-charcoal/50 leading-relaxed">{s.summary}</p>
                  {s.keywords?.length ? (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {s.keywords.map((k) => (
                        <span
                          key={k}
                          className="text-[11px] px-3 py-1 rounded-full bg-moss/8 text-moss border border-moss/15"
                        >
                          {k}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

