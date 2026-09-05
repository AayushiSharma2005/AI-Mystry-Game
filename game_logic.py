"""
game_logic.py
Handles loading content pools and generating a fresh randomized case
every time the player starts a new game.
"""

import json
import random
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "game_data.json")


def load_pool():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_case_titles():
    pool = load_pool()
    return [c["title"] for c in pool["cases"]]

def generate_new_case(selected_title=None):
    """
    Builds a fresh randomized case from the restructured JSON:
    - gets the 5 case-specific suspects
    - marks exactly one as guilty
    - spawns ONLY the guilty suspect's breaking clue + red herrings
    """
    pool = load_pool()

    if selected_title and selected_title != "Random Case":
        case_meta = next((c for c in pool["cases"] if c["title"] == selected_title), random.choice(pool["cases"]))
    else:
        case_meta = random.choice(pool["cases"])
        
    suspects = case_meta["suspects"]
    guilty = random.choice(suspects)

    red_herrings = [c for c in pool.get("clues", []) if c["type"] == "red_herring"]
    random.shuffle(red_herrings)

    case_suspects = {}

    for s in suspects:
        is_guilty = s["id"] == guilty["id"]
        
        # We store the breaking clue on the suspect object for evaluation later.
        # But we only add it to the "discoverable_clues" if they are guilty.
        breaking_clue = s["breaking_clue"]

        case_suspects[s["id"]] = {
            "id": s["id"],
            "name": s["name"],
            "role": s["role"],
            "avatar": s["avatar"],
            "personality": s["personality"],
            "is_guilty": is_guilty,
            "alibi_text": s["alibi_text"],
            "breaking_clue": breaking_clue, 
            "statements": [],  # conversation log for this suspect
        }

    # Build the discoverable clue pool for this case:
    # the one breaking clue (tied to guilty suspect) + 2 red herrings
    discoverable_clues = [guilty["breaking_clue"]] + red_herrings[:2]
    random.shuffle(discoverable_clues)

    return {
        "case_title": case_meta["title"],
        "case_context": case_meta["victim_context"],
        "suspects": case_suspects,
        "guilty_id": guilty["id"],
        "all_case_clues": discoverable_clues,   # clues available to "find" this case
        "found_clues": [],                      # clues the player has actually collected
        "questions_asked": 0,
        "actions_remaining": 20,
        "solved": False,
        "won": None,
    }


def find_random_clue(case_state):
    """Reveal one clue the player hasn't found yet (simulates 'investigate' action)."""
    remaining = [c for c in case_state["all_case_clues"] if c not in case_state["found_clues"]]
    if not remaining:
        return None
    clue = random.choice(remaining)
    case_state["found_clues"].append(clue)
    return clue
