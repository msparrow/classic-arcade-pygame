"""
This module handles loading and saving high scores for the Pygame Arcade.

Scores are stored in a JSON file named 'high_scores.json'.
"""

import json
import os

# The name of the file where high scores are stored.
SCORE_FILE = "high_scores.json"

def load_scores():
    """
    Loads scores from the JSON file.

    Returns:
        dict: A dictionary containing the high scores, with game names as keys.
              Returns an empty dictionary if the file doesn't exist or is invalid.
    """
    if not os.path.exists(SCORE_FILE):
        return {}
    try:
        with open(SCORE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Handle cases where the file is empty or corrupted.
        return {}

def save_score(game_name, new_score):
    """
    Saves a new score if it's higher than the existing one for that game.

    Args:
        game_name (str): The name of the game.
        new_score (int or float): The new score to save.
    """
    # Don't save zero, negative, or invalid scores.
    if not isinstance(new_score, (int, float)) or new_score <= 0:
        return

    scores = load_scores()
    current_high_score = scores.get(game_name, 0)

    # Only save the score if it's a new high score.
    if new_score > current_high_score:
        scores[game_name] = new_score
        with open(SCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=4)
