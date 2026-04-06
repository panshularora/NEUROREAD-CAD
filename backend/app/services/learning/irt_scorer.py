"""
Item Response Theory (IRT) Scorer

This module implements online Item Response Theory using the 
2-Parameter Logistic (2PL) model.

WHY 2PL IS BETTER THAN THE CURRENT DISCRETE SYSTEM (1/2/3):
1. Continuous Scale: Maps ability (theta) and difficulty on an infinite numeric line, 
   offering far more precision than three broad buckets.
2. Population Calibration: Rather than guessing how hard an exercise is, the model 
   self-calibrates difficulty empirically over many students' attempts.
3. Response-Time Awareness: Capable of modifying ability gradients based on reaction 
   times. A correct but slow answer means less mastery than a correct, rapid answer.
4. Separation of Ability & Difficulty: Decouples the learner's skill from the 
   exercise's intrinsic difficulty, eliminating confounding effects.
"""

import math
from typing import Dict, Any


def estimate_ability_update(
    current_ability: float, 
    item_difficulty: float, 
    is_correct: bool, 
    response_time_ms: int, 
    learning_rate: float = 0.3
) -> float:
    """
    Updates the student's ability (theta) using gradient ascent on the 2PL model's
    log-likelihood, incorporating response time modifiers to penalize or forgive.
    
    Math:
    P(correct) = 1 / (1 + exp(-(ability - difficulty)))
    gradient = observation - P(correct)  (where observation is 1 if correct else 0)
    theta_new = theta_old + learning_rate * gradient * time_modifier
    """
    # 2PL Model: Probability of correct response
    p_correct = 1.0 / (1.0 + math.exp(-(current_ability - item_difficulty)))
    
    # Calculate the basic gradient: diff between observation and prediction
    observation = 1.0 if is_correct else 0.0
    base_gradient = observation - p_correct
    
    # Response time modifier logic
    time_modifier = 1.0
    if is_correct:
        if response_time_ms < 1500:
            # Fast and correct: full confidence in the update
            time_modifier = 1.0
        elif response_time_ms > 5000:
            # Slow and correct: reduced confidence, they might have struggled
            time_modifier = max(0.1, 1.0 - ((response_time_ms - 5000) / 10000.0))
    else:
        if response_time_ms < 800:
            # Incorrect and extremely fast: impulsive/careless slip, not necessarily ignorance.
            # Reduce the penalty gradient.
            time_modifier = 0.5
        # If slow and incorrect, standard penalty applies (time_modifier = 1.0)
            
    # Apply learning update
    new_ability = current_ability + (learning_rate * base_gradient * time_modifier)
    
    # Clamp to [-4.0, 4.0] to prevent ability explosions
    return max(-4.0, min(4.0, new_ability))


def calibrate_item_difficulty(
    item_difficulty: float, 
    child_ability: float, 
    is_correct: bool, 
    rate: float = 0.05
) -> float:
    """
    Adjusts the intrinsic difficulty of an exercise based on the child's response.
    
    Math:
    Opposite direction of the ability update. If a highly able child gets it wrong,
    it means the item is harder than we thought. If a low ability child gets it right,
    the item might be easier than calculated.
    """
    # 2PL Probability calculation
    p_correct = 1.0 / (1.0 + math.exp(-(child_ability - item_difficulty)))
    
    observation = 1.0 if is_correct else 0.0
    
    # Gradient for difficulty is inverted: if they got it right (obs 1),
    # the gradient is negative, so difficulty goes down (becomes easier).
    difficulty_gradient = p_correct - observation
    
    new_difficulty = item_difficulty + (rate * difficulty_gradient)
    
    return max(-4.0, min(4.0, new_difficulty))


def ability_to_level(ability: float) -> Dict[str, Any]:
    """
    Maps an infinite IRT theta value to a human-readable scale.
    
    Uses approximation of normal CDF: percentile = Φ(ability).
    Math: percentile ≈ 0.5 * (1 + erf(ability / sqrt(2)))
    """
    # Gaussian CDF approximation using math.erf
    percentile = 0.5 * (1.0 + math.erf(ability / math.sqrt(2.0)))
    
    # Map theta into 5 discrete levels for UI
    if ability < -1.5:
        level = 1
        desc = "Emerging Reader"
    elif ability < -0.5:
        level = 2
        desc = "Developing Reader"
    elif ability < 0.5:
        level = 3
        desc = "Intermediate Reader"
    elif ability < 1.5:
        level = 4
        desc = "Proficient Reader"
    else:
        level = 5
        desc = "Advanced Reader"
        
    return {
        "level": level,
        "percentile": round(percentile * 100, 1),
        "description": desc
    }
