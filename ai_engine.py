"""
ai_engine.py
Wraps two AI-driven capabilities:
  1. generate_dialogue()      -> in-character suspect response to a player's question
  2. check_contradiction()    -> checks a suspect's statements against collected clues

Works with OpenAI or Gemini (auto-detects based on which API key is set in .env).
If no API key is found, falls back to a lightweight offline mock so the game is
still fully playable/demoable without any API cost.
"""

import os
import random
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

PROVIDER = "offline"
client = None
gemini_client = None
import_error = None

if OPENAI_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        PROVIDER = "openai"
    except ImportError:
        import_error = "OpenAI SDK not installed. Run: pip install openai"
elif GEMINI_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_KEY)
        PROVIDER = "gemini"
    except ImportError:
        import_error = "Gemini SDK (google-genai) not installed. Run: pip install google-genai"

GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
]

def _call_gemini(contents):
    """Tries multiple active Gemini models in order so quota/demand issues on one model never block the player."""
    last_err = None
    for model_name in GEMINI_MODELS:
        try:
            resp = gemini_client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            if resp and resp.text:
                return resp.text.strip()
        except Exception as e:
            last_err = e
            print(f"[ai_engine] Model {model_name} failed: {e}. Trying next model...")
            continue
    raise last_err or RuntimeError("All Gemini models failed")

def _parse_api_error(e):
    error_str = str(e)
    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
        return "API Quota Exceeded (Please wait a minute and try again)."
    elif "404" in error_str:
        return "Model Not Found (Check model name configuration)."
    elif "403" in error_str or "401" in error_str:
        return "Invalid API Key or Permission Denied."
    else:
        return f"{type(e).__name__}: {error_str.split('.')[0]}"

# ---------------------------------------------------------------------------
# Dialogue generation
# ---------------------------------------------------------------------------

def generate_dialogue(suspect, question):
    """
    suspect: dict with name, role, personality, alibi_text, is_guilty
    question: player's free-text question
    Returns: a short, in-character response string.
    """
    system_prompt = f"""You are roleplaying as a murder-mystery suspect being interrogated by a detective.

Name: {suspect['name']}
Role: {suspect['role']}
Personality: {suspect['personality']}
Your claimed alibi: "{suspect['alibi_text']}"
You are {"GUILTY" if suspect['is_guilty'] else "INNOCENT"} but must never admit this directly.

Rules:
- Stay fully in character based on the personality given.
- Answer the detective's specific question naturally, while keeping your answer consistent with your claimed alibi.
- Keep your answer to 1-3 short sentences, natural spoken dialogue, no stage directions.
- Never break character or mention you are an AI.
- If guilty, you may sound slightly defensive or over-explain, but never confess outright.
- CRITICAL: You must provide your response in English, followed immediately by its Hindi translation in brackets. Use conversational Hindi (written in either English script/Hinglish or Devanagari). Example: "I was at home. (Main ghar par tha.)"
"""

    if PROVIDER == "offline":
        return _offline_dialogue(suspect, question, error=import_error)

    try:
        if PROVIDER == "openai":
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                max_tokens=150,
                temperature=0.8,
            )
            return resp.choices[0].message.content.strip()

        elif PROVIDER == "gemini":
            return _call_gemini(f"{system_prompt}\n\nDetective asks: {question}")

    except Exception as e:
        print(f"[ai_engine] All API calls failed: {e}")
        return _offline_dialogue(suspect, question)


def _offline_dialogue(suspect, question, error=None):
    """Fallback that acts like a local offline game and directly answers the question type without repeating."""
    q_lower = question.lower().strip()
    alibi = suspect['alibi_text']
    
    if any(w in q_lower for w in ["see", "saw", "look", "dekha", "notice"]):
        return f"I didn't see anything unusual at all. Remember, {alibi} (Maine kuch ajeeb nahi dekha. Yaad rakho, {alibi})"
    elif any(w in q_lower for w in ["where", "location", "place", "kahan", "jagah"]):
        return f"I was right where I claimed to be: {alibi} (Main wahin thi jahan maine bataya: {alibi})"
    elif any(w in q_lower for w in ["who", "anyone", "someone", "kaun", "kisi"]):
        return f"I didn't run into anyone. As I told you, {alibi} (Meri kisi se mulaqaat nahi hui. Jaise maine kaha, {alibi})"
    elif any(w in q_lower for w in ["why", "reason", "kyun", "wajah"]):
        return f"There's no hidden motive here. {alibi} (Yahan koi chupa hua maqsad nahi hai. {alibi})"
    elif any(w in q_lower for w in ["call", "phone", "cctv", "camera", "proof", "evidence", "saboot"]):
        return f"That doesn't change my story one bit. {alibi} (Is se meri baat bilkul nahi badalti. {alibi})"
    else:
        options = [
            f"Regarding \"{question.strip()}\": my story hasn't changed. {alibi} (\"{question.strip()}\" ke baare mein: meri baat wahi hai. {alibi})",
            f"I already answered that as best as I can. {alibi} (Main iska jawab pehle hi de chuka hoon. {alibi})",
            f"You're barking up the wrong tree. {alibi} (Tum galat shakhs par shak kar rahe ho. {alibi})"
        ]
        return random.choice(options)


# ---------------------------------------------------------------------------
# Contradiction Checking (for normal questions)
# ---------------------------------------------------------------------------

def check_contradiction(suspect, latest_statement, found_clues):
    """
    Checks if the suspect's latest statement in dialogue contradicts any collected clues.
    Returns: (has_contradiction: bool, explanation: str)
    """
    if not found_clues or not latest_statement:
        return False, ""

    clues_text = "\n".join([f"- {c['text']}" for c in found_clues])
    
    explanation_prompt = f"""You are an AI detective assistant analyzing a murder mystery interrogation.
Suspect Name: {suspect['name']}
The suspect just said in response to the detective:
"{latest_statement}"

The detective has collected these clues:
{clues_text}

Task:
Did the suspect's statement above DIRECTLY contradict any of the collected clues?
Rules:
- Only flag YES if what the suspect ACTUALLY said in this specific statement clashes with a clue.
- If the suspect's statement does NOT mention, claim, or touch upon the subject of the clue, reply strictly with "NO".
- If the suspect's statement does NOT contradict any clue, reply strictly with "NO".
- If it DOES directly contradict a clue, reply with "YES" followed by one short sentence explaining the exact contradiction.
"""

    if PROVIDER == "offline":
        return False, ""

    try:
        if PROVIDER == "openai":
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": explanation_prompt}],
                max_tokens=60,
                temperature=0.0,
            )
            ans = resp.choices[0].message.content.strip()
        elif PROVIDER == "gemini":
            ans = _call_gemini(explanation_prompt)
            
        if ans.startswith("YES"):
            explanation = ans[3:].lstrip(" :-.")
            return True, explanation
        return False, ""
    except Exception as e:
        print(f"[ai_engine] check_contradiction API call failed: {e}")
        return False, ""


# ---------------------------------------------------------------------------
# Evidence Evaluation (Presenting Clues)
# ---------------------------------------------------------------------------

def evaluate_evidence(suspect, presented_clue):
    """
    suspect: dict with name, role, personality, alibi_text, breaking_clue
    presented_clue: dict representing the clue the player chose to present
    Returns: (is_correct_break: bool, response: str)
    """
    breaking_clue = suspect.get("breaking_clue")
    
    # Check if the presented clue is actually the one that breaks this suspect's alibi
    is_correct_break = False
    if breaking_clue and presented_clue["id"] == breaking_clue["id"]:
        is_correct_break = True

    if is_correct_break:
        system_prompt = f"""You are roleplaying as a murder-mystery suspect being interrogated.
Name: {suspect['name']}
Your claimed alibi: "{suspect['alibi_text']}"
The detective just presented undeniable evidence that breaks your alibi: "{presented_clue['text']}"

Rules:
- You are caught in your lie! You must panic, sound cornered, or defensively confess.
- Keep your answer to 1-2 short sentences.
- CRITICAL: Provide your response in English, followed by its Hindi translation in brackets. Example: "How did you find that?! (Tumhe yeh kaise mila?!)"
"""
    else:
        system_prompt = f"""You are roleplaying as a murder-mystery suspect being interrogated.
Name: {suspect['name']}
Your claimed alibi: "{suspect['alibi_text']}"
The detective just presented irrelevant evidence: "{presented_clue['text']}"

Rules:
- You are unimpressed. Mock the detective, act confused, or dismiss the evidence as irrelevant to your alibi.
- Stay in character ({suspect['personality']}).
- Keep your answer to 1-2 short sentences.
- CRITICAL: Provide your response in English, followed by its Hindi translation in brackets. Example: "What does this have to do with me? (Mera is se kya lena dena?)"
"""

    if PROVIDER == "offline":
        if is_correct_break:
            fallback_msg = f"You got me... I lied about my alibi. (Tumne mujhe pakad liya... Maine jhooth bola tha.)"
        else:
            fallback_msg = f"That proves nothing about my whereabouts. (Is se mere baare mein kuch sabit nahi hota.)"
        return is_correct_break, fallback_msg

    try:
        if PROVIDER == "openai":
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=80,
                temperature=0.8,
            )
            return is_correct_break, resp.choices[0].message.content.strip()

        elif PROVIDER == "gemini":
            ans = _call_gemini(system_prompt)
            return is_correct_break, ans

    except Exception as e:
        print(f"[ai_engine] Evidence evaluation API call failed: {e}")
        fallback = "You got me... I lied. (Tumne mujhe pakad liya...)" if is_correct_break else "That proves nothing! (Is se kuch sabit nahi hota!)"
        return is_correct_break, fallback