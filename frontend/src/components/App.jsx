import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { simplifyText } from '../api/simplify';
import AssistiveMode from './AssistiveMode';
import Hero from './Hero';
import History, { DEFAULT_HISTORY } from './History';
import LearningMode from './LearningMode';
import Navbar from './Navbar';
import SimplifierModal from './SimplifierModal';

function safeGsap() {
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  if (!gsap || !ScrollTrigger) return null;
  try {
    gsap.registerPlugin(ScrollTrigger);
    return { gsap, ScrollTrigger };
  } catch {
    return null;
  }
}

function nextDifficulty(current) {
  const v = (current || '').toLowerCase();
  if (v === 'high') return 'Moderate';
  if (v === 'moderate') return 'Low';
  return 'Low';
}

export default function App() {
  const [mode, setMode] = useState('assistive');
  const [simplifierOpen, setSimplifierOpen] = useState(false);

  const [userId, setUserId] = useState('demo-user-001');
  const [profile, setProfile] = useState('Default');
  const [inputText, setInputText] = useState('');

  const [dyslexiaOn, setDyslexiaOn] = useState(false);
  const [audioOn, setAudioOn] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [metrics, setMetrics] = useState(null);
  const [simplifiedText, setSimplifiedText] = useState('');

  const [expandedHistoryId, setExpandedHistoryId] = useState(null);
  const [historySessions, setHistorySessions] = useState([]);

  const ttsUtteranceRef = useRef(null);

  useEffect(() => {
    // keep original HTML baseline state for history sessions (static list is rendered in History.jsx)
    // live sessions are prepended here.
    setHistorySessions([]);
  }, []);

  useEffect(() => {
    const gs = safeGsap();
    if (!gs) return;
    const { gsap } = gs;

    const ctx = gsap.context(() => {
      gsap.fromTo('.hero-anim', { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 1.2, stagger: 0.15, ease: 'power3.out', delay: 0.2 });
      gsap.fromTo(
        '.impact-card',
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, stagger: 0.15, ease: 'power3.out', scrollTrigger: { trigger: '#impact', start: 'top 75%' } }
      );
      gsap.fromTo(
        '.number-reveal',
        { opacity: 0, scale: 0.5, filter: 'blur(10px)' },
        { opacity: 1, scale: 1, filter: 'blur(0px)', duration: 1, ease: 'back.out(1.5)', scrollTrigger: { trigger: '.number-reveal', start: 'top 85%' } }
      );
      gsap.fromTo(
        '.history-row',
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, stagger: 0.07, ease: 'power2.out', scrollTrigger: { trigger: '#history', start: 'top 80%' } }
      );
    });

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    window.Iconify?.scan?.();
  }, [mode, simplifierOpen, historySessions.length]);

  const impactSection = useMemo(() => {
    return (
      <section id="impact" className="py-32 bg-cream relative z-20 rounded-t-[3rem] -mt-10 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-20">
            <span className="font-mono text-xs text-moss uppercase tracking-wider block mb-3">The Mission</span>
            <h2 className="md:text-5xl text-charcoal text-4xl font-medium tracking-tight max-w-2xl">
              How It Works &amp; Community Impact
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="impact-card col-span-1 md:col-span-2 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col relative overflow-hidden group transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] opacity-0">
              <div className="flex items-center gap-4 mb-6 relative z-10">
                <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center border border-moss/5">
                  <span className="iconify text-xl text-moss" data-icon="solar:scanner-linear" data-inline="false" />
                </div>
                <h3 className="font-medium text-2xl md:text-3xl tracking-tight text-charcoal">Dynamic Adaptation</h3>
              </div>
              <p className="text-charcoal/70 text-base md:text-lg leading-relaxed max-w-lg relative z-10 mt-auto">
                AI that instantly simplifies complex text and adjusts typography based on the reader's unique cognitive needs.
              </p>
            </div>
            <div className="impact-card col-span-1 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col relative overflow-hidden group transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] opacity-0">
              <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center border border-moss/5 mb-6">
                <span className="iconify text-xl text-moss" data-icon="solar:layers-minimalistic-linear" data-inline="false" />
              </div>
              <h3 className="font-medium text-xl md:text-2xl tracking-tight text-charcoal mb-4">Multi-Modal Processing</h3>
              <p className="text-charcoal/70 text-sm leading-relaxed mt-auto">
                Seamlessly integrates Text-to-Speech, keyword extraction, and visual phonics on the fly without breaking focus.
              </p>
            </div>
            <div className="impact-card col-span-1 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col relative overflow-hidden group transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] opacity-0">
              <div className="number-reveal font-medium text-6xl text-moss mb-6 leading-none inline-block" style={{ filter: 'blur(10px)' }}>
                1 in 5
              </div>
              <h3 className="font-medium text-xl tracking-tight text-charcoal mb-3">Dyslexia Support</h3>
              <p className="text-charcoal/70 text-sm leading-relaxed mt-auto">
                Empowering individuals globally with dyslexia by providing frictionless, low-stress reading environments.
              </p>
            </div>
            <div className="impact-card col-span-1 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col relative overflow-hidden group transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] opacity-0">
              <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center border border-moss/5 mb-6">
                <span className="iconify text-xl text-clay" data-icon="solar:diploma-linear" data-inline="false" />
              </div>
              <h3 className="font-medium text-xl tracking-tight text-charcoal mb-3">Educational Equity</h3>
              <p className="text-charcoal/70 text-sm leading-relaxed mt-auto">
                Giving early learners and children the interactive phonics and spelling tools they need to build confidence.
              </p>
            </div>
            <div className="impact-card col-span-1 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col relative overflow-hidden group transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] opacity-0">
              <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center border border-moss/5 mb-6">
                <span className="iconify text-xl text-moss" data-icon="solar:earth-linear" data-inline="false" />
              </div>
              <h3 className="font-medium text-xl tracking-tight text-charcoal mb-3">Universal Accessibility</h3>
              <p className="text-charcoal/70 text-sm leading-relaxed mt-auto">
                Democratizing access to dense legal, medical, and technical documents for the general public.
              </p>
            </div>
          </div>
        </div>
      </section>
    );
  }, []);

  const setModeSafe = useCallback((nextMode) => setMode(nextMode), []);

  const closeSimplifier = useCallback(() => {
    setSimplifierOpen(false);
    setAudioOn(false);
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }, []);

  const toggleDyslexia = useCallback(() => setDyslexiaOn((v) => !v), []);

  const toggleAudio = useCallback(() => {
    setAudioOn((v) => !v);
  }, []);

  useEffect(() => {
    if (!audioOn) {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      return;
    }

    const txt = simplifiedText || '';
    const placeholder = 'Simplified text will appear here once you run an analysis.';
    if (!txt || txt === placeholder || !window.speechSynthesis) {
      setAudioOn(false);
      return;
    }

    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(txt);
    ttsUtteranceRef.current = u;
    u.onend = () => setAudioOn(false);
    window.speechSynthesis.speak(u);

    return () => {
      try {
        window.speechSynthesis.cancel();
      } catch {
        // ignore
      }
    };
  }, [audioOn, simplifiedText]);

  const runSimplifier = useCallback(async () => {
    const text = inputText.trim();
    if (!text) {
      setError('Please enter some text to simplify.');
      return;
    }

    setError('');
    setLoading(true);
    setSimplifiedText('');
    setMetrics(null);

    try {
      const data = await simplifyText(text, profile);
      setSimplifiedText(data.simplifiedText || '');
      setMetrics(data);

      const dateStr = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      setHistorySessions((prev) => {
        const n = prev.length + 1;
        const difficultyTo = nextDifficulty(data.difficulty);
        const live = {
          id: `live-${Date.now()}`,
          title: `Live Session ${n}`,
          date: dateStr,
          originalScore: data.originalScore,
          simplifiedScore: data.intensity,
          reduction: data.reduction,
          difficultyFrom: data.difficulty,
          difficultyTo,
          summary: data.impactSummary,
          keywords: data.keywords,
          accent: 'clay',
          isNew: true,
        };
        return [live, ...prev];
      });
    } catch (e) {
      setError('Error: Could not reach the API. Please try again.');
      // eslint-disable-next-line no-console
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [inputText, profile]);

  const modesSection = (
    <section id="modes" className="py-24 bg-cream relative z-20 overflow-hidden">
      <div className="max-w-7xl mr-auto ml-auto pr-6 pl-6">
        <div className="flex justify-center mb-16">
          <div className="bg-moss/5 p-1 rounded-full inline-flex relative shadow-inner" id="mode-tabs">
            <div
              className="absolute top-1 bottom-1 left-1 w-[calc(50%-4px)] bg-white rounded-full shadow-sm transition-transform duration-500 ease-spring"
              id="tab-indicator"
              style={{ transform: mode === 'assistive' ? 'translateX(0)' : 'translateX(100%)' }}
            />
            <button
              id="tab-assistive"
              type="button"
              onClick={() => setModeSafe('assistive')}
              className={`relative z-10 px-6 md:px-10 py-3 rounded-full text-xs md:text-sm font-medium tracking-wide transition-colors w-40 md:w-56 text-center ${
                mode === 'assistive' ? 'text-charcoal' : 'text-charcoal/40 hover:text-charcoal/80'
              }`}
            >
              Assistive Mode
            </button>
            <button
              id="tab-learning"
              type="button"
              onClick={() => setModeSafe('learning')}
              className={`md:px-10 md:text-sm transition-colors md:w-56 text-xs font-medium tracking-wide text-center w-40 z-10 rounded-full pt-3 pr-6 pb-3 pl-6 relative ${
                mode === 'learning' ? 'text-charcoal' : 'text-charcoal/40 hover:text-charcoal/80'
              }`}
            >
              Learning Mode
            </button>
          </div>
        </div>

        <div className="grid" style={{ gridTemplateColumns: '1fr', gridTemplateRows: '1fr' }}>
          <AssistiveMode active={mode === 'assistive'} onOpenSimplifier={() => setSimplifierOpen(true)} />
          <LearningMode active={mode === 'learning'} childId={userId} />
        </div>
      </div>
    </section>
  );

  const allHistorySessions = useMemo(() => [...historySessions, ...DEFAULT_HISTORY], [historySessions]);

  return (
    <div className="bg-cream text-charcoal font-sans antialiased overflow-x-hidden selection:bg-moss selection:text-cream">
      <div className="noise-overlay" />

      <SimplifierModal
        open={simplifierOpen}
        onClose={closeSimplifier}
        userId={userId}
        onUserIdChange={setUserId}
        profile={profile}
        onProfileChange={setProfile}
        inputText={inputText}
        onInputTextChange={setInputText}
        dyslexiaOn={dyslexiaOn}
        onToggleDyslexia={toggleDyslexia}
        audioOn={audioOn}
        onToggleAudio={toggleAudio}
        simplifiedText={simplifiedText}
        loading={loading}
        metrics={metrics}
        error={error}
        onRunSimplifier={runSimplifier}
      />

      <Navbar mode={mode} onModeChange={setModeSafe} />
      <Hero />
      {impactSection}
      {modesSection}

      {/* History: render live sessions first (prepend), then the original static sessions inside History component */}
      <History sessions={allHistorySessions} expandedId={expandedHistoryId} onToggleExpanded={setExpandedHistoryId} />
    </div>
  );
}

