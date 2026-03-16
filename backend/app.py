"""
AI-Based Exam Anxiety Detector
Flask Backend - Main Application
"""

import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_model import analyze_anxiety

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Exam Anxiety Detector API is running."})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    POST /analyze
    Body:    { "text": "<student input>" }
    Returns: { "anxiety_level", "confidence_score", "message", "tips", "signals" }
    """
    data = request.get_json(silent=True)

    if not data or "text" not in data:
        logger.warning("Request received with no text field.")
        return jsonify({"error": "Request body must contain a 'text' field."}), 400

    text = data["text"].strip()
    if len(text) < 10:
        logger.warning("Text too short: %d chars", len(text))
        return jsonify({"error": "Please enter at least 10 characters."}), 400

    logger.info("Analyzing text (%d chars): %.80s...", len(text), text)

    result = analyze_anxiety(text)

    if "error" in result:
        logger.error("AI processing error: %s", result["error"])
        return jsonify(result), 500

    logger.info(
        "Result → level=%s  confidence=%.2f",
        result.get("anxiety_level"),
        result.get("confidence_score", 0),
    )
    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting server on http://localhost:%d", port)
    app.run(debug=True, host="0.0.0.0", port=port)
