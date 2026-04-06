import { useEffect, useMemo, useState } from 'react';

export default function Navbar({ mode, onModeChange }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const className = useMemo(() => {
    const base =
      'fixed top-6 left-1/2 -translate-x-1/2 z-50 transition-all duration-500 rounded-full px-6 py-3 flex items-center justify-between w-[90%] max-w-5xl border';
    if (!scrolled) return `${base} bg-transparent text-cream border-transparent`;
    return `${base} bg-white/60 backdrop-blur-md text-moss border-moss/10`;
  }, [scrolled]);

  return (
    <nav id="navbar" className={className}>
      <div className="uppercase text-sm font-medium tracking-[0.2em]">N e u r o r e a d</div>
      <div className="hidden md:flex items-center gap-8 font-medium text-xs tracking-wide uppercase">
        <a
          href="#modes"
          onClick={(e) => {
            e.preventDefault();
            onModeChange('assistive');
            document.getElementById('modes')?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="hover:opacity-70 transition-opacity"
          aria-current={mode === 'assistive' ? 'page' : undefined}
        >
          ASSIST
        </a>
        <a
          href="#modes"
          onClick={(e) => {
            e.preventDefault();
            onModeChange('learning');
            document.getElementById('modes')?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="hover:opacity-70 transition-opacity"
          aria-current={mode === 'learning' ? 'page' : undefined}
        >
          LEARNING
        </a>
      </div>
    </nav>
  );
}

