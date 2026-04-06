"""
Bayesian Knowledge Tracing (BKT) Engine

This module implements the Hidden Markov Model formulation of BKT from Corbett & Anderson (1994).
It tracks the probability that a student "knows" a specific skill over time.
"""

import random
from dataclasses import dataclass
from typing import Dict, Any

# Full skill taxonomy with calibrated priors.
# Hard confusions like bd_medial have lower initial knowledge and slower learning priors.
SKILL_PRIORS = {
    "bd_initial": {"p_know": 0.40, "p_learn": 0.15, "p_slip": 0.20, "p_guess": 0.25},
    "bd_final": {"p_know": 0.30, "p_learn": 0.12, "p_slip": 0.25, "p_guess": 0.25},
    "bd_medial": {"p_know": 0.20, "p_learn": 0.10, "p_slip": 0.30, "p_guess": 0.25},
    "pq_initial": {"p_know": 0.35, "p_learn": 0.15, "p_slip": 0.20, "p_guess": 0.25},
    "pq_final": {"p_know": 0.25, "p_learn": 0.12, "p_slip": 0.25, "p_guess": 0.25},
    "mn_initial": {"p_know": 0.50, "p_learn": 0.20, "p_slip": 0.10, "p_guess": 0.25},
    "mn_final": {"p_know": 0.45, "p_learn": 0.20, "p_slip": 0.15, "p_guess": 0.25},
    "vowel_ae": {"p_know": 0.40, "p_learn": 0.18, "p_slip": 0.15, "p_guess": 0.33},
    "vowel_eo": {"p_know": 0.40, "p_learn": 0.18, "p_slip": 0.15, "p_guess": 0.33},
    "vowel_ui": {"p_know": 0.35, "p_learn": 0.15, "p_slip": 0.20, "p_guess": 0.33},
}

@dataclass
class SkillBelief:
    skill_id: str
    p_know: float
    p_learn: float
    p_slip: float
    p_guess: float
    attempt_count: int = 0

    def update(self, is_correct: bool) -> 'SkillBelief':
        """
        Updates the belief state using the standard BKT forward algorithm.
        
        Math:
        1. Posterior conditional probability (Bayes' Theorem):
           If correct: P(L|obs) = P(L)*(1-slip) / [P(L)*(1-slip) + (1-P(L))*guess]
           If incorrect: P(L|obs) = P(L)*slip / [P(L)*slip + (1-P(L))*(1-guess)]
        2. Expected knowledge state after learning opportunity:
           p_know_next = P(L|obs) + (1 - P(L|obs)) * P(T)
           where P(T) is p_learn (probability of transition).
        """
        # Step 1: Compute posterior based on observation
        if is_correct:
            numerator = self.p_know * (1.0 - self.p_slip)
            denominator = numerator + (1.0 - self.p_know) * self.p_guess
        else:
            numerator = self.p_know * self.p_slip
            denominator = numerator + (1.0 - self.p_know) * (1.0 - self.p_guess)
        
        # Avoid division by zero in edge cases
        if denominator == 0:
            posterior = 0.0
        else:
            posterior = numerator / denominator

        # Step 2: Add learning probability
        p_know_next = posterior + (1.0 - posterior) * self.p_learn
        
        # Construct and return updated dataclass
        return SkillBelief(
            skill_id=self.skill_id,
            p_know=p_know_next,
            p_learn=self.p_learn,
            p_slip=self.p_slip,
            p_guess=self.p_guess,
            attempt_count=self.attempt_count + 1
        )

    @property
    def is_mastered(self) -> bool:
        """
        Mastery threshold. True when the probability of knowing is >= 0.95.
        """
        return self.p_know >= 0.95

    @property
    def confusion_priority(self) -> float:
        """
        A metric defining how badly the student is confused about this skill.
        Used for basic greedy selection criteria or tracking weakest points.
        """
        return 1.0 - self.p_know


def select_next_skill(beliefs: Dict[str, SkillBelief]) -> str:
    """
    Selects the next skill using Thompson Sampling from Beta distributions.
    
    Instead of greedily picking the skill with the highest confusion (lowest p_know),
    we parameterize a Beta distribution: Beta(alpha, beta) where:
    alpha ~ represents evidence of failure (confusion) = (1 - p_know) * scale
    beta ~ represents evidence of success = p_know * scale
    
    We sample from this distribution for all skills. The skill that yields the 
    highest sample value is selected. This inherently balances exploitation 
    (focusing on unmastered skills) with exploration (occasionally reviewing others).
    """
    best_skill = None
    max_sample = -1.0
    scale = 10.0  # Controls the variance of the Beta distribution

    for skill_id, belief in beliefs.items():
        # Alpha is tied to confusion (1.0 - p_know), Beta is tied to knowledge
        # Add 1.0 to ensure alpha, beta > 0 (requirement for beta distribution)
        alpha = (1.0 - belief.p_know) * scale + 1.0
        beta_val = belief.p_know * scale + 1.0
        
        # Sample probability of this skill being the best focus directly
        sample = random.betavariate(alpha, beta_val)
        
        if sample > max_sample:
            max_sample = sample
            best_skill = skill_id
            
    # Fallback just in case beliefs is empty
    return best_skill if best_skill else list(beliefs.keys())[0]


def load_child_beliefs(error_patterns: Dict[str, float]) -> Dict[str, SkillBelief]:
    """
    Bootstraps BKT state from the legacy dictionary format ({"b_d_confusion": 0.7}).
    
    If the child had a high error rate in the legacy format, we apply a penalty 
    to the starting p_know of the calibrated priors for that group of skills.
    """
    beliefs = {}
    
    # Map legacy patterns to the new precise skill IDs
    legacy_mapping = {
        "b_d_confusion": ["bd_initial", "bd_medial", "bd_final"],
        "p_q_confusion": ["pq_initial", "pq_final"],
        "m_n_confusion": ["mn_initial", "mn_final"],
    }
    
    for skill_id, priors in SKILL_PRIORS.items():
        p_know = priors["p_know"]
        
        # Look up if any legacy error pattern applies to this skill
        for legacy_key, target_skills in legacy_mapping.items():
            if skill_id in target_skills and legacy_key in error_patterns:
                # Prior error rate exists. 
                # If error_rate is 0.7, we dramatically drop initial p_know
                error_rate = error_patterns[legacy_key]
                p_know = max(0.01, p_know - (error_rate * 0.5))

        beliefs[skill_id] = SkillBelief(
            skill_id=skill_id,
            p_know=p_know,
            p_learn=priors["p_learn"],
            p_slip=priors["p_slip"],
            p_guess=priors["p_guess"],
            attempt_count=0
        )
        
    return beliefs
