/**
 * ExamMind — AI Exam Anxiety Detector
 * Frontend Script
 */

// ── Config ────────────────────────────────────────────────────────────────────
const API_URL = "http://localhost:5000/analyze";

const SAMPLES = [
  "I feel pretty calm about tomorrow's exam. I've studied consistently this week and understand the main topics. A little nervous, but mostly confident in my preparation.",
  "I'm worried about the exam tomorrow. There are some topics I haven't fully revised and I keep second-guessing myself. I'm not sleeping well and feeling quite tense, but trying to stay positive.",
  "I can't stop panicking. My mind goes completely blank whenever I try to revise. I haven't slept properly in two days, my heart keeps racing and I genuinely feel like I'm going to fail everything. I feel completely overwhelmed and don't know what to do anymore."
];

const LEVEL_CONFIG = {
  Low: {
    emoji: "😌", subtext: "Minimal stress detected — you are managing well",
    sigClass: "chip chip-green"
  },
  Moderate: {
    emoji: "😟", subtext: "Noticeable stress signals — consider support strategies",
    sigClass: "chip chip-yellow"
  },
  High: {
    emoji: "😰", subtext: "Significant distress detected — please seek support",
    sigClass: "chip chip-red"
  }
};

// ── DOM refs ──────────────────────────────────────────────────────────────────
const textarea     = document.getElementById("studentText");
const charCount    = document.getElementById("charCount");
const analyzeBtn   = document.getElementById("analyzeBtn");
const btnSpinner   = document.getElementById("btnSpinner");
const btnLabel     = document.getElementById("btnLabel");
const loadingBar   = document.getElementById("loadingBar");
const errorBanner  = document.getElementById("errorBanner");
const errorMsg     = document.getElementById("errorMsg");
const resultSection = document.getElementById("resultSection");

// ── Character counter ─────────────────────────────────────────────────────────
textarea.addEventListener("input", () => {
  const n = textarea.value.length;
  charCount.textContent = `${n} character${n !== 1 ? "s" : ""}`;
});

// ── Sample buttons ────────────────────────────────────────────────────────────
document.querySelectorAll(".sample-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const idx = parseInt(btn.dataset.idx, 10);
    textarea.value = SAMPLES[idx];
    textarea.dispatchEvent(new Event("input"));
    hideError();
  });
});

// ── Analyse ───────────────────────────────────────────────────────────────────
analyzeBtn.addEventListener("click", runAnalysis);

textarea.addEventListener("keydown", e => {
  if (e.ctrlKey && e.key === "Enter") runAnalysis();
});

async function runAnalysis() {
  const text = textarea.value.trim();

  if (!text) {
    showError("Please enter some text before analysing.");
    return;
  }
  if (text.length < 10) {
    showError("Please enter at least 10 characters for a meaningful analysis.");
    return;
  }

  setLoading(true);
  hideError();
  resultSection.hidden = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Server error: ${response.status}`);
    }

    const data = await response.json();
    renderResult(data);

  } catch (err) {
    console.error("Analysis error:", err);

    if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
      showError("Cannot reach the backend. Make sure Flask is running on localhost:5000.");
    } else {
      showError(err.message || "Analysis failed. Please try again.");
    }
  } finally {
    setLoading(false);
  }
}

// ── Render result ─────────────────────────────────────────────────────────────
function renderResult(data) {
  const level  = data.anxiety_level || "Low";
  const conf   = parseFloat(data.confidence_score || 0.8);
  const cfg    = LEVEL_CONFIG[level] || LEVEL_CONFIG.Low;
  const lvlKey = level.toLowerCase();

  // Header
  const icon = document.getElementById("levelIcon");
  icon.textContent = cfg.emoji;
  icon.className   = `level-icon ${lvlKey}`;

  const nameEl = document.getElementById("levelName");
  nameEl.textContent = `${level.toUpperCase()} ANXIETY`;
  nameEl.className   = `level-name ${lvlKey}`;

  document.getElementById("levelSub").textContent = cfg.subtext;

  const badge = document.getElementById("confBadge");
  badge.textContent = `CONFIDENCE: ${Math.round(conf * 100)}%`;
  badge.className   = `conf-badge ${lvlKey}`;

  // Score bars  (derive from confidence + level)
  const scores = computeScores(level, conf);
  setTimeout(() => {
    setBar("barLow",  "pctLow",  scores.low);
    setBar("barMod",  "pctMod",  scores.moderate);
    setBar("barHigh", "pctHigh", scores.high);
  }, 80);

  // Message
  document.getElementById("resultMessage").textContent = data.message || "";

  // Signals
  const signals = Array.isArray(data.signals) ? data.signals : [];
  const sigList = document.getElementById("signalsList");
  sigList.innerHTML = signals.length
    ? signals.map(s => `<span class="signal-tag ${cfg.sigClass}">${s}</span>`).join("")
    : `<span style="font-size:12px;color:var(--muted)">No specific signals extracted.</span>`;

  // Tips
  const tips = Array.isArray(data.tips) ? data.tips : [];
  document.getElementById("tipsGrid").innerHTML = tips
    .map(t => `<div class="tip-card">
      <span class="tip-icon">${t.icon || "💡"}</span>
      <span class="tip-text">${t.text || t}</span>
    </div>`).join("");

  // Show
  resultSection.hidden = false;
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function computeScores(level, conf) {
  const high = Math.round(conf * 100);
  const rest = 100 - high;

  if (level === "Low")      return { low: high, moderate: Math.round(rest * 0.6), high: Math.round(rest * 0.4) };
  if (level === "Moderate") return { low: Math.round(rest * 0.5), moderate: high, high: Math.round(rest * 0.5) };
  return { low: Math.round(rest * 0.3), moderate: Math.round(rest * 0.7), high };
}

function setBar(barId, pctId, value) {
  document.getElementById(barId).style.width = `${value}%`;
  document.getElementById(pctId).textContent = `${value}%`;
}

function setLoading(on) {
  analyzeBtn.disabled    = on;
  btnSpinner.style.display = on ? "block" : "none";
  btnLabel.textContent   = on ? "ANALYSING…" : "ANALYSE TEXT";
  loadingBar.style.display = on ? "block" : "none";
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorBanner.hidden = false;
}

function hideError() {
  errorBanner.hidden = true;
}
