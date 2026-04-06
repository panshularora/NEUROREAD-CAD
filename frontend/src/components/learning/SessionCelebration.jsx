export default function SessionCelebration({ sessionId, endReason }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="w-32 h-32 rounded-full bg-moss/20 flex items-center justify-center mb-8">
        <span className="iconify text-6xl text-moss" data-icon="solar:cup-star-bold" />
      </div>
      <h2 className="text-5xl font-opendyslexic font-bold text-cream mb-4">Journey Complete!</h2>
      <p className="text-xl text-cream/80 max-w-lg leading-relaxed">
        {endReason === 'fatigue' 
          ? "You worked really hard! It's good to take a rest now."
          : "Amazing job today! Your brain grew a little stronger."}
      </p>
    </div>
  );
}
