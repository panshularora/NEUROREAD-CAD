/**
 * Learning Mode dashboard: Daily Mission, XP bar, progress, and 4 feature cards.
 * Dyslexia-friendly dark theme with soft orange (clay) accents. Framer Motion for microinteractions.
 */
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Mic,
  PenSquare,
  Brain,
  BookOpen,
  ChevronRight,
  Flame,
  Star,
} from 'lucide-react';
import { getLearningProgress } from '../../services/api';

const CARD_STAGGER = 0.08;
const CARD_HOVER = { scale: 1.02, y: -4 };
const CARD_TAP = { scale: 0.98 };

interface LearningDashboardProps {
  childId: string;
  onOpenModule: (module: 'phonics' | 'spelling' | 'comprehension' | 'reading') => void;
}

const cards = [
  {
    id: 'phonics' as const,
    title: 'Interactive Phonics',
    description: 'Tap letters to hear sounds. See phoneme breakdown and waveform.',
    icon: Mic,
    color: 'clay',
    progress: 0.6,
  },
  {
    id: 'spelling' as const,
    title: 'Spelling Trainer',
    description: 'Drag letters to build words. Voice input and instant feedback.',
    icon: PenSquare,
    color: 'clay',
    progress: 0.4,
  },
  {
    id: 'comprehension' as const,
    title: 'Comprehension Lab',
    description: 'Quiz cards with immediate feedback and difficulty scaling.',
    icon: Brain,
    color: 'clay',
    progress: 0.5,
  },
  {
    id: 'reading' as const,
    title: 'Guided Reading',
    description: 'Word-by-word highlighting. Tap a word to hear it. Adjust speed.',
    icon: BookOpen,
    color: 'clay',
    progress: 0.3,
  },
];

export default function LearningDashboard({ childId, onOpenModule }: LearningDashboardProps) {
  const [xp, setXp] = useState(0);
  const [level, setLevel] = useState(1);
  const [streak, setStreak] = useState(0);
  const [dailyMission, setDailyMission] = useState('Complete 3 phonics exercises');
  const [metrics, setMetrics] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getLearningProgress(childId)
      .then((res) => {
        if (cancelled) return;
        setXp(res.total_xp ?? 0);
        setLevel(res.learning_level ?? 1);
        setStreak(res.streak_days ?? 0);
        setMetrics(res.progress_metrics ?? {});
        if (res.recommendations?.length) {
          const focus = res.recommendations.find((r) => r.type === 'focus');
          if (focus) setDailyMission(focus.message);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [childId]);

  const xpForNextLevel = 100 + level * 50;
  const xpProgress = Math.min(1, xp / xpForNextLevel);

  return (
    <div className="relative z-10 space-y-8">
      {/* Daily Mission + XP + Avatar row */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-cream/5 border border-cream/10 p-6 flex flex-col sm:flex-row gap-6 items-start sm:items-center"
      >
        <div className="w-16 h-16 rounded-2xl bg-clay/20 border border-clay/30 flex items-center justify-center shrink-0">
          <Star className="w-8 h-8 text-clay" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-cream/50 uppercase tracking-wider mb-1">Daily Mission</p>
          <p className="text-cream font-medium text-lg">{loading ? '…' : dailyMission}</p>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-clay" />
            <span className="text-cream font-medium">{streak}</span>
            <span className="text-cream/50 text-sm">day streak</span>
          </div>
          <div className="text-right">
            <p className="text-cream/50 text-xs">Level {level}</p>
            <p className="text-clay font-semibold">{xp} XP</p>
          </div>
        </div>
      </motion.div>

      {/* XP progress bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="space-y-2"
      >
        <div className="flex justify-between text-sm">
          <span className="text-cream/60">Progress to next level</span>
          <span className="text-cream">{xp} / {xpForNextLevel} XP</span>
        </div>
        <div className="h-3 rounded-full bg-cream/10 overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-clay to-clay/80"
            initial={{ width: 0 }}
            animate={{ width: `${xpProgress * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>
      </motion.div>

      {/* 4 feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {cards.map((card, i) => {
          const Icon = card.icon;
          const progressPct = card.id in metrics ? Math.round((metrics[card.id] ?? 0) * 100) : Math.round((card.progress ?? 0) * 100);
          return (
            <motion.button
              key={card.id}
              type="button"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * CARD_STAGGER }}
              whileHover={CARD_HOVER}
              whileTap={CARD_TAP}
              onClick={() => onOpenModule(card.id)}
              className="text-left border border-cream/10 bg-cream/[0.03] rounded-2xl p-6 flex flex-col md:flex-row gap-6 items-start hover:bg-cream/[0.06] hover:border-clay/20 transition-colors group"
            >
              <div className="w-14 h-14 shrink-0 rounded-2xl bg-clay/10 flex items-center justify-center border border-clay/20 group-hover:scale-105 transition-transform">
                <Icon className="w-7 h-7 text-clay" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-xl tracking-tight text-cream mb-2">{card.title}</h3>
                <p className="text-sm text-cream/50 leading-relaxed mb-4">{card.description}</p>
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1 h-2 rounded-full bg-cream/10 overflow-hidden max-w-[120px]">
                    <motion.div
                      className="h-full rounded-full bg-clay/60"
                      initial={{ width: 0 }}
                      animate={{ width: `${progressPct}%` }}
                      transition={{ duration: 0.5, delay: 0.3 + i * 0.05 }}
                    />
                  </div>
                  <span className="text-cream/60 text-xs">{progressPct}%</span>
                  <ChevronRight className="w-5 h-5 text-clay/70 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
