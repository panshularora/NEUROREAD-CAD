export default function Hero() {
  return (
    <header className="relative h-[100dvh] w-full overflow-hidden flex items-end">
      <div className="absolute inset-0 w-full h-full">
        <img
          src="https://images.unsplash.com/photo-1470115636492-6d2b56f9146d?q=80&w=2070&auto=format&fit=crop"
          className="w-full h-full object-cover object-center"
          alt="Dark Forest"
        />
        <div className="bg-gradient-to-b from-moss/40 via-moss/80 to-charcoal absolute top-0 right-0 bottom-0 left-0" />
      </div>
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 pb-24 md:pb-32">
        <div className="max-w-4xl hero-content">
          <h1 className="flex flex-col gap-2">
            <span className="hero-anim md:text-7xl lg:text-[6rem] text-cream leading-none text-5xl font-medium tracking-tighter mt-2">
              Reading, Reimagined
            </span>
            <span className="hero-anim md:text-8xl lg:text-[8rem] text-cream leading-none text-6xl font-medium tracking-tight mt-2 pr-4 italic">
              for Every Mind..
            </span>
          </h1>
          <p className="hero-anim text-cream/70 md:text-base leading-relaxed text-sm max-w-md mt-10">
            AI that adapts reading for every mind — helping children learn and adults understand complex text
            with ease.
          </p>
        </div>
      </div>
    </header>
  );
}

