import math


def estimate_elo(winrate, known_elo):
    """Estimate ELO based on win rate."""
    if winrate in [0, 1]:  # Prevent log(0) issues
        winrate = max(min(winrate, 0.99), 0.01)
    return known_elo - 400 * math.log10((1 - winrate) / winrate)