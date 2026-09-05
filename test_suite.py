"""
test_suite.py
Comprehensive automated test suite for NOIR - AI Detective Mystery.
Run anytime with:
    python test_suite.py
"""

import sys
import json
import os

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure local directory is on import path
sys.path.insert(0, os.path.dirname(__file__))

import game_logic
import ai_engine

def run_tests():
    total_passed = 0
    total_tests = 7

    print("=" * 65)
    print("🕵️  CATCH THE LIE — AUTOMATED BUG & INTEGRITY VERIFICATION SUITE")
    print("=" * 65)

    # -------------------------------------------------------------
    # TEST 1: Database Schema & Case Integrity
    # -------------------------------------------------------------
    print("\n[TEST 1/7] Checking Database Schema & Cases Integrity...")
    pool = game_logic.load_pool()
    cases = pool.get("cases", [])
    assert len(cases) >= 6, f"Expected at least 6 cases, found {len(cases)}"
    
    total_suspects = 0
    for c in cases:
        assert "title" in c and "victim_context" in c and "suspects" in c
        assert len(c["suspects"]) == 5, f"Case {c['title']} must have exactly 5 suspects"
        for s in c["suspects"]:
            total_suspects += 1
            for field in ["id", "name", "role", "avatar", "personality", "alibi_text", "breaking_clue"]:
                assert field in s, f"Suspect {s.get('name')} missing field {field}"
            bc = s["breaking_clue"]
            assert "id" in bc and "text" in bc and bc["type"] == "breaking"
            # Verify clue text is specific and not generic
            assert len(bc["text"]) > 10, f"Breaking clue text too short: {bc['text']}"

    assert total_suspects == 30, f"Expected 30 total suspects across 6 cases, found {total_suspects}"
    print(f"  ✅ PASSED: 6 cases & all 30 unique suspects verified with airtight schema.")
    total_passed += 1

    # -------------------------------------------------------------
    # TEST 2: Specific Case Selection & Randomization
    # -------------------------------------------------------------
    print("\n[TEST 2/7] Checking Case Selection & Guilt Randomization...")
    titles = game_logic.get_all_case_titles()
    assert len(titles) == 6

    for title in titles:
        case = game_logic.generate_new_case(title)
        assert case["case_title"] == title
        assert len(case["suspects"]) == 5
        assert case["guilty_id"] in case["suspects"]
        assert case["actions_remaining"] == 20
        # Exactly 1 guilty suspect
        guilty_count = sum(1 for s in case["suspects"].values() if s["is_guilty"])
        assert guilty_count == 1
        # Exactly 1 breaking clue + 2 red herrings = 3 discoverable clues
        assert len(case["all_case_clues"]) == 3
        breaking_in_case = [clue for clue in case["all_case_clues"] if clue["type"] == "breaking"]
        assert len(breaking_in_case) == 1
        assert breaking_in_case[0]["id"] == case["suspects"][case["guilty_id"]]["breaking_clue"]["id"]

    print(f"  ✅ PASSED: All 6 cases generate with exactly 1 guilty culprit and corresponding breaking clue.")
    total_passed += 1

    # -------------------------------------------------------------
    # TEST 3: Crime Scene Investigation Logic
    # -------------------------------------------------------------
    print("\n[TEST 3/7] Checking Clue Discovery Mechanics...")
    case = game_logic.generate_new_case()
    collected = []
    for _ in range(3):
        clue = game_logic.find_random_clue(case)
        assert clue is not None
        assert clue not in collected
        collected.append(clue)
    assert len(case["found_clues"]) == 3
    # 4th search must return None (scene fully searched)
    assert game_logic.find_random_clue(case) is None
    print("  ✅ PASSED: Clue collection properly reveals clues and stops when depleted.")
    total_passed += 1

    # -------------------------------------------------------------
    # TEST 4: Live AI Dialogue Generation & Multi-Model Fallback
    # -------------------------------------------------------------
    print("\n[TEST 4/7] Checking Live AI Dialogue Generation...")
    case = game_logic.generate_new_case("The Midnight Heist")
    test_suspect = list(case["suspects"].values())[0]
    
    question = "Where were you at the time of the heist?"
    reply = ai_engine.generate_dialogue(test_suspect, question)
    assert reply is not None and len(reply.strip()) > 5
    # Must NOT have technical error or mock prefix
    assert "[API Limit Hit" not in reply
    assert "[AI ERROR" not in reply
    print(f"  Response received: \"{reply[:75]}...\"")
    print("  ✅ PASSED: Dialogue generation succeeded with clean in-character response.")
    total_passed += 1

    # -------------------------------------------------------------
    # TEST 5: Contradiction Detection Accuracy
    # -------------------------------------------------------------
    print("\n[TEST 5/7] Checking Contradiction Detection Precision...")
    suspect_test = {
        "name": "Mrs. Sharma",
        "alibi_text": "I was greeting guests in the reception area.",
        "is_guilty": True,
    }
    breaking_clue = [{
        "id": "C_VB5",
        "text": "Several guests mentioned Groom's mother Mrs. Sharma was completely missing from the reception line.",
        "type": "breaking"
    }]

    # Case A: Irrelevant question answer -> must NOT trigger contradiction
    safe_statement = "She merely muttered some absolute nonsense about not belonging in this family."
    has_contra, exp = ai_engine.check_contradiction(suspect_test, safe_statement, breaking_clue)
    assert not has_contra, f"False positive! Contradiction incorrectly flagged on: {safe_statement}"

    # Case B: Contradictory statement -> MUST trigger contradiction
    clashing_statement = "I was right out in the grand reception area, graciously welcoming our esteemed guests all evening."
    has_contra, exp = ai_engine.check_contradiction(suspect_test, clashing_statement, breaking_clue)
    assert has_contra, "False negative! Contradiction was NOT flagged on a clashing statement!"
    print(f"  Explanation returned: \"{exp}\"")
    print("  ✅ PASSED: Contradiction check accurately avoids false positives and detects true contradictions.")
    total_passed += 1

    # -------------------------------------------------------------
    # TEST 6: Evidence Presentation (Ace Attorney Mechanic)
    # -------------------------------------------------------------
    print("\n[TEST 6/7] Checking Evidence Presentation Mechanics...")
    guilty_suspect = {
        "name": "Night Guard Jai Kumar",
        "role": "Night Guard",
        "personality": "Sleepy, defensive",
        "alibi_text": "I was doing my hourly rounds on the second floor.",
        "breaking_clue": {
            "id": "C_MH2",
            "text": "The electronic badge log shows Night Guard Jai Kumar never left the ground floor desk."
        }
    }
    wrong_clue = {"id": "R1", "text": "A torn ticket stub was found near the side entrance."}

    # Present wrong clue -> must be rejected
    is_break, resp = ai_engine.evaluate_evidence(guilty_suspect, wrong_clue)
    assert not is_break, "Wrong clue was incorrectly accepted as breaking clue!"
    assert "[AI ERROR" not in resp

    # Present right clue -> must break the suspect
    is_break, resp = ai_engine.evaluate_evidence(guilty_suspect, guilty_suspect["breaking_clue"])
    assert is_break, "Correct breaking clue was rejected!"
    assert "[AI ERROR" not in resp
    print(f"  Cornered reaction: \"{resp[:75]}...\"")
    print("  ✅ PASSED: Evidence presentation correctly corners culprits and rejects irrelevant clues.")
    total_passed += 1

    # -------------------------------------------------------------
    # TEST 7: Local Offline Fallback Stability
    # -------------------------------------------------------------
    print("\n[TEST 7/7] Checking Offline Fallback Stability...")
    offline_reply = ai_engine._offline_dialogue(test_suspect, "Did you see anyone near the vault?")
    assert offline_reply is not None
    assert "[API Limit Hit" not in offline_reply
    assert "[AI ERROR" not in offline_reply
    assert test_suspect["alibi_text"] in offline_reply
    print(f"  Offline reply: \"{offline_reply[:75]}...\"")
    print("  ✅ PASSED: Offline fallback operates smoothly without technical banners.")
    total_passed += 1

    print("\n" + "=" * 65)
    print(f"🎉 ALL {total_passed}/{total_tests} TESTS PASSED! ZERO BUGS DETECTED.")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
