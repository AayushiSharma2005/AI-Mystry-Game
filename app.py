"""
app.py
AI Detective Mystery - Streamlit game entrypoint.
Run with: streamlit run app.py
"""

import streamlit as st
from game_logic import generate_new_case, find_random_clue, get_all_case_titles
from ai_engine import generate_dialogue, evaluate_evidence, check_contradiction

st.set_page_config(
    page_title="Catch The Lie | AI Detective Mystery",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# THEME / CUSTOM CSS  -- noir detective look: dark charcoal + amber accents
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 20% 0%, #1c1a17 0%, #0e0d0c 55%, #08080a 100%);
    color: #e9e2d0;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* Title styling */
.noir-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #e7b94c;
    letter-spacing: 0.5px;
    margin-bottom: 0;
    text-shadow: 0 0 18px rgba(231, 185, 76, 0.25);
}
.noir-subtitle {
    color: #9a927e;
    font-size: 1rem;
    margin-top: 4px;
    margin-bottom: 1.4rem;
    font-style: italic;
}

/* Card component */
.noir-card {
    background: linear-gradient(145deg, #1a1815, #131211);
    border: 1px solid #3a342a;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    margin-bottom: 1rem;
}

.case-banner {
    background: linear-gradient(120deg, #221c14, #17140f);
    border-left: 4px solid #e7b94c;
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.2rem;
}
.case-banner h3 {
    color: #e7b94c;
    font-family: 'Playfair Display', serif;
    margin: 0 0 6px 0;
}
.case-banner p {
    color: #b8ae96;
    margin: 0;
    font-size: 0.92rem;
}

/* Suspect chip */
.suspect-chip {
    display:flex; align-items:center; gap:10px;
    background:#161310; border:1px solid #332d22; border-radius:10px;
    padding:10px 12px; margin-bottom:8px; transition: all 0.15s ease;
}
.suspect-chip.active {
    border-color:#e7b94c; background:#221b0f;
    box-shadow: 0 0 12px rgba(231,185,76,0.15);
}
.suspect-avatar {
    font-size:1.5rem; width:38px; height:38px; border-radius:50%;
    background:#26211a; display:flex; align-items:center; justify-content:center;
    border: 1px solid #3a342a;
}
.suspect-name { font-weight:600; color:#eee6d3; font-size:0.93rem; margin:0;}
.suspect-role { color:#8f8770; font-size:0.76rem; margin:0;}

/* Chat bubbles */
.bubble-row { display:flex; margin-bottom:10px; }
.bubble-detective {
    margin-left:auto; background:#e7b94c; color:#1a1611;
    padding:10px 16px; border-radius:16px 16px 4px 16px; max-width:70%;
    font-size:0.92rem; font-weight:500;
}
.bubble-suspect {
    background:#201c17; border:1px solid #362f24; color:#e9e2d0;
    padding:10px 16px; border-radius:16px 16px 16px 4px; max-width:70%;
    font-size:0.92rem;
}
.bubble-alert {
    background:#3a1414; border:1px solid #7a2a2a; color:#ff9d9d;
    padding:10px 16px; border-radius:12px; max-width:80%;
    font-size:0.88rem; margin: 6px 0 14px 0;
}

/* Clue tag */
.clue-tag {
    display:inline-block; background:#1c2419; border:1px solid #3a4a2c;
    color:#c3e3a4; padding:6px 12px; border-radius:8px; font-size:0.82rem;
    margin: 4px 6px 4px 0;
}
.clue-tag.red-herring {
    background:#241c14; border:1px solid #4a3a2c; color:#e3c3a4;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(145deg, #e7b94c, #cf9f34);
    color: #1a1611; font-weight:600; border:none; border-radius:8px;
    padding: 0.5rem 1.2rem; box-shadow: 0 4px 14px rgba(231,185,76,0.25);
    transition: all 0.15s ease;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(231,185,76,0.4);
}

.stTextInput>div>div>input {
    background:#161310; color:#e9e2d0; border:1px solid #3a342a; border-radius:8px;
}

.result-win {
    background: linear-gradient(145deg, #16281a, #0f1c12);
    border: 1px solid #2e5a37; border-radius:14px; padding:2rem; text-align:center;
}
.result-lose {
    background: linear-gradient(145deg, #2a1414, #1c0f0f);
    border: 1px solid #5a2e2e; border-radius:14px; padding:2rem; text-align:center;
}
.result-win h2 { color:#7ee08a; font-family:'Playfair Display', serif; }
.result-lose h2 { color:#e08a8a; font-family:'Playfair Display', serif; }

hr { border-color: #2a251d; }

/* Mobile responsiveness */
@media (max-width: 768px) {
    .noir-title { font-size: 1.8rem; }
    .noir-subtitle { font-size: 0.85rem; margin-bottom: 1rem; }
    .noir-card { padding: 1rem; }
    .case-banner { padding: 0.9rem; }
    .bubble-detective, .bubble-suspect { max-width: 90%; font-size: 0.88rem; }
    .suspect-chip { padding: 8px 10px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE INIT
# ---------------------------------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "intro"
if "case" not in st.session_state:
    st.session_state.case = None
if "active_suspect" not in st.session_state:
    st.session_state.active_suspect = None
if "case_number" not in st.session_state:
    st.session_state.case_number = 1


def start_new_case(selected_case=None):
    st.session_state.case = generate_new_case(selected_case)
    st.session_state.active_suspect = list(st.session_state.case["suspects"].keys())[0]
    st.session_state.screen = "investigate"


# ---------------------------------------------------------------------------
# HEADER (shown on every screen)
# ---------------------------------------------------------------------------
st.markdown('<p class="noir-title">🕵️ CATCH THE LIE — AI Detective Mystery</p>', unsafe_allow_html=True)
st.markdown('<p class="noir-subtitle">Ask the right questions. Catch the lie. Name the guilty.</p>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SCREEN 1: INTRO
# ---------------------------------------------------------------------------
if st.session_state.screen == "intro":
    st.markdown('<div class="noir-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <h3 style="color:#e7b94c; font-family:'Playfair Display', serif;">Case #{st.session_state.case_number}</h3>
    <p style="color:#b8ae96;">A new randomized mystery every time you play — five suspects,
    one liar, and a handful of clues scattered between them. Question everyone,
    catch the contradiction, and make your accusation before time runs out.</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    case_titles = ["Random Case"] + get_all_case_titles()
    selected_case = st.selectbox("Select a Mystery to Solve:", options=case_titles)

    if st.button("🔎 Start Investigation", use_container_width=True):
        start_new_case(selected_case)
        st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 2: INVESTIGATE (interrogation)
# ---------------------------------------------------------------------------
elif st.session_state.screen == "investigate":
    case = st.session_state.case

    st.markdown(f"""
    <div class="case-banner">
        <h3>{case['case_title']}</h3>
        <p>{case['case_context']}</p>
        <p style="color:#8a8270; font-size:0.85rem; margin-top:8px;"><em>💡 Tip: You can question the suspects in any order. Ask them where they were or who they saw, and investigate the scene to find evidence that breaks their story!</em></p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📝 Detective's Notepad")
        st.text_area("Jot down lies and suspicions here...", height=400, key="notepad")

    if case["actions_remaining"] <= 0:
        st.error("⏰ Time's up! The police chief took you off the case.")
        st.session_state.screen = "accuse"
        st.rerun()

    col_left, col_right = st.columns([1, 2.2])

    with col_left:
        st.markdown(f"**ACTIONS REMAINING: {case['actions_remaining']}**")
        st.markdown("---")
        st.markdown("**SUSPECTS**")
        for sid, s in case["suspects"].items():
            active_class = "active" if sid == st.session_state.active_suspect else ""
            st.markdown(f"""
            <div class="suspect-chip {active_class}">
                <div class="suspect-avatar">{s['avatar']}</div>
                <div>
                    <p class="suspect-name">{s['name']}</p>
                    <p class="suspect-role">{s['role']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Question {s['name'].split()[0]}", key=f"select_{sid}", use_container_width=True):
                st.session_state.active_suspect = sid
                st.rerun()

        st.markdown("---")
        st.markdown("**EVIDENCE BOARD**")
        if case["found_clues"]:
            for c in case["found_clues"]:
                cls = "clue-tag" if c["type"] == "breaking" else "clue-tag red-herring"
                st.markdown(f'<span class="{cls}">🔎 {c["text"]}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#7a725e; font-size:0.85rem;">No evidence collected yet.</p>', unsafe_allow_html=True)

        if st.button("🔍 Investigate the scene", use_container_width=True):
            case["actions_remaining"] -= 1
            clue = find_random_clue(case)
            if clue:
                st.toast(f"New clue found: {clue['text']}", icon="🔎")
            else:
                st.toast("No more clues left to find here.", icon="🧩")
            st.rerun()

        st.markdown("---")
        if st.button("⚖️ Ready to accuse", use_container_width=True):
            st.session_state.screen = "accuse"
            st.rerun()

    with col_right:
        active = case["suspects"][st.session_state.active_suspect]
        st.markdown(f"### Interrogating: {active['avatar']} {active['name']} — *{active['role']}*")

        chat_container = st.container(height=340)
        with chat_container:
            for turn in active["statements"]:
                st.markdown(f'<div class="bubble-row"><div class="bubble-detective">{turn["q"]}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bubble-row"><div class="bubble-suspect">{turn["a"]}</div></div>', unsafe_allow_html=True)
                if turn.get("contradiction"):
                    st.markdown(f'<div class="bubble-alert">⚠️ Contradiction flagged: {turn["contradiction"]}</div>', unsafe_allow_html=True)

        clicked_suggestion = None
        with st.expander("💡 Need ideas? Suggested Questions", expanded=False):
            st.markdown("<small style='color:#b8ae96;'>Click any question to ask it immediately, or type your own below:</small>", unsafe_allow_html=True)
            suggested_qs = [
                "Where were you at the time of the incident?",
                "Did you notice anyone or anything unusual?",
                "What was your relationship with the victim?",
                "Can anyone verify your whereabouts?",
            ]
            s_col1, s_col2 = st.columns(2)
            for idx, sq in enumerate(suggested_qs):
                target_col = s_col1 if idx % 2 == 0 else s_col2
                with target_col:
                    if st.button(f"🔍 {sq}", key=f"sq_btn_{idx}", use_container_width=True):
                        clicked_suggestion = sq

        question = st.text_input("Ask your own question:", key="question_input", placeholder="e.g. Where were you at 10 PM last night?")
        c1, c2 = st.columns([1, 5])
        with c1:
            ask_clicked = st.button("Ask ➤")

        chosen_q = clicked_suggestion if clicked_suggestion else (question.strip() if (ask_clicked and question.strip()) else None)

        if chosen_q:
            case["actions_remaining"] -= 1
            with st.spinner(f"{active['name']} is responding..."):
                answer = generate_dialogue(active, chosen_q)
                has_contra, explanation = check_contradiction(active, answer, case["found_clues"])

            active["statements"].append({
                "q": chosen_q,
                "a": answer,
                "contradiction": explanation if has_contra else None,
            })
            case["questions_asked"] += 1
            st.rerun()
            
        st.markdown("---")
        if case["found_clues"]:
            st.markdown("##### Present Evidence")
            # Create a dictionary mapping clue text to clue dict
            clue_options = {f"🔎 {c['text']}": c for c in case["found_clues"]}
            selected_clue_text = st.selectbox("Select evidence to present to this suspect:", options=list(clue_options.keys()), label_visibility="collapsed")
            
            if st.button("Present Clue 📑"):
                case["actions_remaining"] -= 1
                presented_clue = clue_options[selected_clue_text]
                with st.spinner(f"Presenting {selected_clue_text}..."):
                    is_correct, answer = evaluate_evidence(active, presented_clue)
                
                active["statements"].append({
                    "q": f"[Presented Evidence]: {presented_clue['text']}",
                    "a": answer,
                    "contradiction": "Caught in a lie!" if is_correct else None
                })
                st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 3: ACCUSE
# ---------------------------------------------------------------------------
elif st.session_state.screen == "accuse":
    case = st.session_state.case
    st.markdown('<div class="noir-card">', unsafe_allow_html=True)
    st.markdown("### Who is guilty?")
    st.markdown('<p style="color:#9a927e;">Review the evidence and name your suspect. Choose carefully — this is final.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    cols = st.columns(len(case["suspects"]))
    for i, (sid, s) in enumerate(case["suspects"].items()):
        with cols[i]:
            st.markdown(f"""
            <div class="noir-card" style="text-align:center;">
                <div style="font-size:2rem;">{s['avatar']}</div>
                <p class="suspect-name">{s['name']}</p>
                <p class="suspect-role">{s['role']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Accuse {s['name'].split()[0]}", key=f"accuse_{sid}", use_container_width=True):
                case["solved"] = True
                case["won"] = (sid == case["guilty_id"])
                case["accused_id"] = sid
                st.session_state.screen = "result"
                st.rerun()

    if st.button("⬅ Back to investigation"):
        st.session_state.screen = "investigate"
        st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 4: RESULT
# ---------------------------------------------------------------------------
elif st.session_state.screen == "result":
    case = st.session_state.case
    guilty = case["suspects"][case["guilty_id"]]
    accused = case["suspects"][case["accused_id"]]

    if case["won"]:
        st.markdown(f"""
        <div class="result-win">
            <h2>✅ Case Solved</h2>
            <p style="color:#cfe8d2;">You correctly identified <b>{guilty['name']}</b> as the guilty party.</p>
            <p style="color:#9ac79f; font-size:0.85rem;">Their alibi: "{guilty['alibi_text']}"<br>
            Broken by: "{guilty['breaking_clue']['text']}"</p>
            <p style="color:#7fae84; font-size:0.85rem; margin-top:10px;">
                {case['questions_asked']} question(s) asked · {len(case['found_clues'])} clue(s) found
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-lose">
            <h2>❌ Wrong Accusation</h2>
            <p style="color:#e8cfcf;">You accused <b>{accused['name']}</b>, but the real culprit was <b>{guilty['name']}</b>.</p>
            <p style="color:#c79a9a; font-size:0.85rem;">Their alibi: "{guilty['alibi_text']}"<br>
            Broken by: "{guilty['breaking_clue']['text']}"</p>
            <p style="color:#ae7f7f; font-size:0.85rem; margin-top:10px;">
                {case['questions_asked']} question(s) asked · {len(case['found_clues'])} clue(s) found
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("🔁 Play a new case", use_container_width=True):
        st.session_state.case_number += 1
        st.session_state.screen = "intro"
        st.session_state.case = None
        st.rerun()
