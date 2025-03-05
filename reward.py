import numpy as np
from scipy import stats

"""
There are two reward functions implemented here:
The first one is reward_zscore, which normalizes the win probabilities using z-scores into the range [0,1],
and returns these normalized values as the rewards. 
This has the benefit of every legal move getting some positive reward,
but comes at the drawback of bad moves still getting some reward.

The second one is reward_clipped, which is a little more complex but does a much better job of distinguishing between good and bad moves.
It first normalizes the win probabilities using z-scores as before, but then sets all moves with a normalized reward below CLIPPING_THRESHOLD to 0.
It then renormalizes the remaining rewards to the range [0,1] and returns these as the rewards.
This has the benefit of only "good" moves getting a reward, but comes at the possible expense of the model getting more infrequent feedback.


I have also included versions that take in a "model_output" parameter, and if the "model_output" is a legal move, it will return the reward for that move.
If it is not a legal move, it will return BAD_OUTPUT_REWARD (intialized to -1) as the reward.

I made these as I wasn't sure how we want the rewards calculated

These second versions call the original versions, so make sure to import correctly if you use them.
"""
CLIPPING_THRESHOLD = 0.5
BAD_OUTPUT_REWARD = -1

def reward_clipped(legal_moves, win_probabilities):
    z_scores = stats.zscore(win_probabilities)
    rewards = clipped_normalize_rewards(z_scores, CLIPPING_THRESHOLD)
    return rewards

def reward_zscore(legal_moves, win_probabilities):
    z_scores = stats.zscore(win_probabilities)
    return normalize_rewards(z_scores)

def reward_clipped_with_model_output(legal_moves, win_probabilities, model_output):
    if model_output in legal_moves:
        return reward_clipped(legal_moves, win_probabilities)[legal_moves.index(model_output)]
    return BAD_OUTPUT_REWARD

def reward_zscore_with_model_output(legal_moves, win_probabilities, model_output):
    if model_output in legal_moves:
        return reward_zscore(legal_moves, win_probabilities)[legal_moves.index(model_output)]
    return BAD_OUTPUT_REWARD


def normalize_rewards(z_scores):
    z_min = np.min(z_scores)
    z_max = np.max(z_scores)
    if z_min == z_max:
        return [1]
    return (z_scores - z_min) / (z_max - z_min)


def clipped_normalize_rewards(z_scores, threshold=0.5):
    z_scores = np.array(z_scores, dtype=float)

    # Step 1: Normalize to range [0, 1]
    z_min = np.min(z_scores)
    z_max = np.max(z_scores)
    
    if np.isclose(z_min, z_max):  # Avoid division by zero
        return np.zeros_like(z_scores)

    normalized = (z_scores - z_min) / (z_max - z_min)

    # Step 2: Apply threshold (set values < threshold to 0)
    normalized[normalized < threshold] = 0

    # Step 3: Renormalize to [0, 1] if necessary
    new_min = np.min(normalized)
    new_max = np.max(normalized)

    if np.isclose(new_min, new_max):  # If all remaining values are the same, return as is
        return np.zeros_like(normalized) if new_max == 0 else np.ones_like(normalized)

    return (normalized - new_min) / (new_max - new_min)
