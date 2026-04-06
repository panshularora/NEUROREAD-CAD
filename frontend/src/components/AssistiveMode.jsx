export default function AssistiveMode({ active, onOpenSimplifier }) {
  return (
    <div
      id="content-assistive"
      className={`col-start-1 row-start-1 transition-all duration-700 ease-spring ${
        active ? 'opacity-100 translate-y-0 z-10' : 'opacity-0 translate-y-8 pointer-events-none z-0'
      }`}
    >
      <div className="mb-12 text-center max-w-2xl mx-auto">
        <span className="font-mono text-xs text-clay uppercase tracking-wider mb-4 block">System 01</span>
        <h2 className="font-medium text-4xl tracking-tight text-charcoal mb-4">Assistive Mode</h2>
        <p className="text-charcoal/70 text-sm md:text-base leading-relaxed">
          For adults and complex text. <span className="italic text-moss text-lg">Enhance comprehension</span>{' '}
          and reduce cognitive load with real-time semantic manipulation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
        <div
          onClick={onOpenSimplifier}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') onOpenSimplifier();
          }}
          className="clickable-card col-span-1 md:col-span-3 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.2)] hover:border-moss/30 group relative"
        >
          <div className="w-14 h-14 rounded-full bg-cream flex items-center justify-center mb-8 border border-moss/5 group-hover:scale-105 transition-transform group-hover:bg-moss group-hover:border-moss">
            <span
              className="iconify text-2xl text-moss group-hover:text-cream"
              data-icon="solar:magic-stick-3-linear"
              data-inline="false"
            />
          </div>
          <h3 className="font-medium text-2xl tracking-tight text-charcoal mb-3">Smart Simplifier</h3>
          <p className="text-sm text-charcoal/60 leading-relaxed max-w-sm">
            Transform complex jargon into clear, accessible language in real-time. Uncover the underlying meaning
            instantly.
          </p>
          <div className="open-badge">
            <span className="iconify" data-icon="solar:arrow-right-linear" style={{ width: '.7rem', height: '.7rem' }} />
            Open Tool
          </div>
        </div>

        <div className="col-span-1 md:col-span-3 border border-moss/10 rounded-[2rem] p-8 md:p-10 bg-white flex flex-col transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] group">
          <div className="w-14 h-14 rounded-full bg-cream flex items-center justify-center mb-8 border border-moss/5 group-hover:scale-105 transition-transform">
            <span className="iconify text-2xl text-moss" data-icon="solar:minimize-square-linear" data-inline="false" />
          </div>
          <h3 className="font-medium text-2xl tracking-tight text-charcoal mb-3">Instant Summarizer</h3>
          <p className="text-sm text-charcoal/60 leading-relaxed max-w-sm">
            Extract the core message. Get the TL;DR of any dense clinical, legal, or technical document instantly.
          </p>
        </div>

        <div className="col-span-1 md:col-span-2 border border-moss/10 rounded-[2rem] p-8 bg-white flex flex-col transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] group">
          <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center mb-6 border border-moss/5 group-hover:scale-105 transition-transform">
            <span className="iconify text-xl text-moss" data-icon="solar:key-linear" data-inline="false" />
          </div>
          <h3 className="font-medium text-xl tracking-tight text-charcoal mb-2">Keyword Extraction</h3>
          <p className="text-sm text-charcoal/60 leading-relaxed">Identify and define crucial terms dynamically as you read.</p>
        </div>

        <div className="col-span-1 md:col-span-2 border border-moss/10 rounded-[2rem] p-8 bg-white flex flex-col transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] group">
          <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center mb-6 border border-moss/5 group-hover:scale-105 transition-transform">
            <span className="iconify text-xl text-moss" data-icon="solar:volume-loud-linear" data-inline="false" />
          </div>
          <h3 className="font-medium text-xl tracking-tight text-charcoal mb-2">Natural Voice TTS</h3>
          <p className="text-sm text-charcoal/60 leading-relaxed">
            Listen to any text with our fluid, human-like Text-to-Speech engine.
          </p>
        </div>

        <div className="col-span-1 md:col-span-2 border border-moss/10 rounded-[2rem] p-8 bg-white flex flex-col transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_-15px_rgba(46,64,54,0.15)] group">
          <div className="w-12 h-12 rounded-full bg-cream flex items-center justify-center mb-6 border border-moss/5 group-hover:scale-105 transition-transform">
            <span className="iconify text-xl text-moss" data-icon="solar:settings-linear" data-inline="false" />
          </div>
          <h3 className="font-medium text-xl tracking-tight text-charcoal mb-2">Accessibility Prefs</h3>
          <p className="text-sm text-charcoal/60 leading-relaxed">Customizable fonts, contrast ratios, and spacing presets.</p>
        </div>
      </div>
    </div>
  );
}

