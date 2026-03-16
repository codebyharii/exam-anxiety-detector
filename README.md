# ExamMind — AI-Based Exam Anxiety Detector

An intelligent mental-wellness web app that analyses student text and classifies exam anxiety as **Low**, **Moderate**, or **High** using NLP preprocessing and Google Gemini AI.

---

## Project Structure

```
exam-anxiety-detector/
├── backend/
│   ├── app.py            ← Flask API server
│   ├── ai_model.py       ← NLP preprocessing + Gemini classification
│   └── requirements.txt  ← Python dependencies
├── frontend/
│   ├── index.html        ← Main UI (pure black theme)
│   ├── style.css         ← Styles
│   └── script.js         ← Frontend logic
└── README.md
```

---

## Setup & Run

### 1. Get a Gemini API Key

- Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- Create a free API key

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Set your API key

**Windows (PowerShell)**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Mac / Linux**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Start the Flask server

```bash
python app.py
```

Server will start at `http://localhost:5000`

### 5. Open the frontend

Open `frontend/index.html` directly in your browser.

> No extra server needed for the frontend — it's plain HTML/CSS/JS.

---

## API Reference

### `GET /`
Health check.

```json
{ "status": "ok", "message": "Exam Anxiety Detector API is running." }
```

### `POST /analyze`

**Request:**
```json
{ "text": "I feel really stressed about my exam tomorrow..." }
```

**Response:**
```json
{
  "anxiety_level": "High",
  "confidence_score": 0.91,
  "message": "It is okay to feel overwhelmed. Please reach out for support.",
  "tips": [
    { "icon": "💬", "text": "Speak with a counselor or mentor — you are not alone." },
    { "icon": "🆘", "text": "Contact your institution's student wellness center today." }
  ],
  "signals": ["overwhelmed", "stressed", "panic", "can't sleep"],
  "method": "gemini"
}
```

---

## How It Works

1. **Student** types pre-exam thoughts into the UI
2. **Frontend** sends text to Flask `/analyze` endpoint
3. **NLP Preprocessing** — lowercase, remove noise, strip stopwords
4. **Gemini AI** classifies anxiety as Low / Moderate / High
5. **Fallback** — if Gemini is unavailable, keyword-based classifier is used
6. **Result** displayed with score bars, signals, and personalised tips

---

## Ethical Disclaimer

> This tool is designed for **supportive purposes only** and does not provide medical diagnosis. Results should not replace professional mental health assessment. Please consult a qualified mental health professional if you are experiencing severe distress.

---

## Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Backend   | Python · Flask · Flask-CORS   |
| AI/NLP    | Google Gemini 1.5 Flash       |
| Frontend  | HTML · CSS · Vanilla JS       |
| Styling   | Custom CSS (pure black theme) |

---

## Team

| Name         | Role      |
|--------------|-----------|
| Hari Omsingh | Team Lead |
| Naman Tyagi  | Member    |
