"""
AI-Based Exam Anxiety Detector
NLP + Gemini AI Model Module (google-genai SDK)
"""

import os
import re
import json
import logging

from google import genai

logger = logging.getLogger(__name__)

# ── Gemini setup ──────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
client = genai.Client(api_key=GEMINI_API_KEY)

# ── Stopwords ─────────────────────────────────────────────────────────────────
STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "he","him","his","she","her","hers","it","its","they","them","their",
    "what","which","who","is","am","are","was","were","be","been","being",
    "have","has","had","do","does","did","will","would","shall","should",
    "may","might","must","can","could","a","an","the","and","but","or","nor",
    "for","yet","so","at","by","in","of","on","to","up","as","into","with",
    "about","above","after","before","between","during","through","under",
}

# ── Tips per level ────────────────────────────────────────────────────────────
TIPS = {
    "Low": [
        {"icon": "📚", "text": "Keep maintaining your healthy revision schedule."},
        {"icon": "🌿", "text": "Stay consistent with sleep and exercise routines."},
        {"icon": "✅", "text": "Review your notes briefly the night before."},
        {"icon": "😊", "text": "Your confidence is an asset — trust your preparation."},
    ],
    "Moderate": [
        {"icon": "🌬️", "text": "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s."},
        {"icon": "⏱️", "text": "Use the Pomodoro technique: 25 min study, 5 min break."},
        {"icon": "🧘", "text": "A 10-minute mindfulness session can reduce cortisol."},
        {"icon": "📝", "text": "Write down your top 3 worry topics and tackle them first."},
    ],
    "High": [
        {"icon": "💬", "text": "Speak with a counselor or mentor — you are not alone."},
        {"icon": "🆘", "text": "Contact your institution's student wellness center today."},
        {"icon": "🛌", "text": "Prioritize sleep above last-minute cramming — rest helps recall."},
        {"icon": "🤝", "text": "Talk to a trusted friend or family member about how you feel."},
    ],
}

MESSAGES = {
    "Low":      "Great mindset! You seem well-prepared. Keep up the calm, focused approach.",
    "Moderate": "You are doing okay — some stress is normal. Use the tips below to stay balanced.",
    "High":     "It is okay to feel overwhelmed. Please reach out for support — you do not have to face this alone.",
}


# ── NLP Preprocessing ─────────────────────────────────────────────────────────
def preprocess_text(text: str) -> str:
    """Lowercase, remove noise, strip stopwords."""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(tokens)


# ── Keyword Fallback ──────────────────────────────────────────────────────────
def keyword_fallback(text: str) -> dict:
    """Lightweight keyword-based classifier used when Gemini is unavailable."""
    text_lower = text.lower()

    high_keywords = [
        "panic","cant breathe","can't breathe","breakdown","hopeless",
        "fail","failed","failing","disaster","doomed","helpless",
        "overwhelmed","terrified","nightmare","no hope","give up",
        "cant sleep","can't sleep","heart racing","shaking","crying",
        "blank mind","mind blank","don't know anything",
    ]
    moderate_keywords = [
        "worried","nervous","stress","stressed","anxious","anxiety",
        "not ready","scared","fear","doubt","unsure","behind",
        "confused","struggling","difficult","hard time","pressure",
        "tense","uneasy","concerned","dread",
    ]

    high_score = sum(1 for kw in high_keywords if kw in text_lower)
    mod_score  = sum(1 for kw in moderate_keywords if kw in text_lower)

    if high_score >= 2 or (high_score >= 1 and mod_score >= 2):
        level, conf = "High", round(0.70 + min(high_score * 0.05, 0.15), 2)
    elif mod_score >= 2 or high_score == 1:
        level, conf = "Moderate", round(0.65 + min(mod_score * 0.04, 0.15), 2)
    else:
        level, conf = "Low", round(0.75 + min((3 - mod_score) * 0.05, 0.20), 2)

    signals = []
    for kw in high_keywords + moderate_keywords:
        if kw in text_lower and kw not in signals:
            signals.append(kw)

    return {
        "anxiety_level":    level,
        "confidence_score": min(conf, 0.97),
        "message":          MESSAGES[level],
        "tips":             TIPS[level],
        "signals":          signals[:5],
        "method":           "keyword_fallback",
    }


# ── Gemini Classification (new google-genai SDK) ──────────────────────────────
SYSTEM_PROMPT = """You are a compassionate AI mental-wellness assistant specializing in
student exam anxiety detection. Analyze the student's text and classify
the exam anxiety level.

Return ONLY a valid JSON object — no markdown, no code fences, no extra text.

JSON schema:
{
  "anxiety_level": "Low" | "Moderate" | "High",
  "confidence_score": <float 0.0-1.0>,
  "reasoning": "<1-2 sentences explaining your classification>",
  "signals": ["<keyword or phrase from text>", ...]
}

Classification guide:
- Low:      calm, prepared, minor nerves, positive framing
- Moderate: worried, stressed, some doubt, sleep issues, pressure
- High:     panic, overwhelmed, hopeless, physical symptoms, catastrophizing
"""


def gemini_classify(text: str) -> dict:
    """Call Gemini API using the new google-genai SDK."""
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Student text:\n\"{text}\"\n\n"
        "Respond ONLY with the JSON object."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    raw = response.text.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"```json|```", "", raw).strip()
    parsed = json.loads(raw)
    return parsed


# ── Main Entry Point ──────────────────────────────────────────────────────────
def analyze_anxiety(raw_text: str) -> dict:
    """
    Full pipeline:
      1. Preprocess text
      2. Classify via Gemini (or fallback to keyword classifier)
      3. Attach tips & message
    """
    cleaned = preprocess_text(raw_text)
    logger.debug("Cleaned text: %s", cleaned)

    # ── Try Gemini first ───────────────────────────────────────────────────────
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        try:
            ai_result = gemini_classify(raw_text)
            level = ai_result.get("anxiety_level", "Low")
            if level not in TIPS:
                level = "Low"

            return {
                "anxiety_level":    level,
                "confidence_score": round(float(ai_result.get("confidence_score", 0.80)), 2),
                "message":          MESSAGES[level],
                "tips":             TIPS[level],
                "signals":          ai_result.get("signals", [])[:5],
                "reasoning":        ai_result.get("reasoning", ""),
                "method":           "gemini",
            }
        except Exception as exc:
            logger.warning("Gemini call failed (%s). Using keyword fallback.", exc)

    # ── Fallback ───────────────────────────────────────────────────────────────
    logger.info("Using keyword fallback classifier.")
    return keyword_fallback(raw_text)