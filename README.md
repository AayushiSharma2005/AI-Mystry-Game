# 🕵️ Catch The Lie

**Catch The Lie** is an interactive AI-powered detective mystery game. Players step into the shoes of an investigator to interrogate suspects, inspect crime scenes for evidence, catch contradictions in suspect statements, and present conclusive proof to crack the case.

---

## 🎮 Gameplay Overview

- **Case Selection**: Choose from multiple thematic mysteries (e.g., *The Missing Painting*, *The Midnight Heist*, *The Ghost Ship*, *The Vanishing Bride*) or opt for a randomized case.
- **Dynamic Interrogation**: Interrogate 5 distinct suspects per case. Suspects respond in-character based on their personality and alibi, delivering dialogue in English with conversational Hindi (Hinglish) translations.
- **Investigate & Collect Evidence**: Search the crime scene to uncover breaking clues and red herrings.
- **Contradiction Detection**: If a suspect makes a claim during questioning that conflicts with discovered evidence, a contradiction is flagged.
- **Present Evidence**: Corner the guilty suspect Ace-Attorney style by presenting the exact piece of evidence that disproves their story.
- **Action Economy**: Every question, scene investigation, and evidence presentation consumes an action point, adding pressure to solve the case before running out of turns.
- **Detective's Notepad**: Integrated notepad in the sidebar to track clues, motives, and observations throughout the investigation.

---

## 🛠 Tech Stack

- **Frontend & Interface**: [Streamlit](https://streamlit.io/) with custom Noir-themed styling and responsive mobile layout.
- **AI Core**: Google Gemini (`google-genai` SDK) with multi-model fallback chain (`gemini-flash-lite-latest`, `gemini-3.8-flash`, etc.) and optional OpenAI integration.
- **Game Engine**: Pure Python state machine with deterministic case generation, clue mapping, and graceful offline fallback.

---

## 📂 Project Structure

```
detective_game/
├── app.py                # Main Streamlit application and UI screens
├── ai_engine.py          # LLM dialogue generation and contradiction verification
├── game_logic.py         # Case generator, suspect routing, and clue management
├── test_suite.py         # Automated test suite
├── data/
│   └── game_data.json    # Mystery database (cases, suspects, alibis, clues)
├── .streamlit/
│   └── config.toml       # Streamlit theme and deployment configuration
├── requirements.txt      # Project dependencies
├── .env.example          # Sample environment variables
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/) *(optional; runs in offline mode if no key is provided)*

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AayushiSharma2005/AI-Mystry-Game.git
   cd AI-Mystry-Game
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory (based on `.env.example`):
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   The game will open in your default browser at `http://localhost:8501`.

---

## 🧪 Running Tests

To run the automated test suite verifying case generation, dialogue flow, evidence evaluation, and contradiction checks:

```bash
python test_suite.py
```
