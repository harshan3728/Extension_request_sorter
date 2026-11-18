# Extension Request Sorter — Capstone Project
**Programme:** CIT AI-Native Engineering Programme, Semester 1  
**Assessment:** Assessment 5 — Capstone Project (40%)  
**Domain:** Higher Education Administration  
**Project Folder:** `Extension-Request-Sorter`  

---

## 📌 Executive Summary
The **Extension Request Sorter** is a professional, reliable, and beginner-explainable AI-powered administrative triage system for university assignment-extension requests. It leverages Groq's high-speed inference engine (`openai/gpt-oss-120b`) strictly for **information extraction and summarization**, paired with a **deterministic Python policy engine** for recommendation sorting.

> **CRITICAL ARCHITECTURAL RULE:** The system **never approves or rejects** requests. Course faculty remain solely responsible for every final decision.

---

## 🏛️ System Architecture

```
[ requests.csv ] + [ courses.csv ]
              │
              ▼
   [ Groq LLM Extractor ] (Extracts: course, days, reason, 15-word privacy summary)
              │
              ▼
 [ Python Validation Layer ] (Ensures JSON schema, whitelist checks, string matching)
              │
              ├── Invalid? ──> Retry Once ──> Safe Fallback (No hallucinated data)
              │
              ▼
  [ Deterministic Policy Engine ] (Python logic evaluates verified facts)
              │
              ├── Missing course or days?       ──> "needs_more_info"
              ├── Days <= 3 AND eligible reason ──> "within_policy"
              └── All other scenarios           ──> "needs_faculty_review"
              │
              ▼
 [ Privacy & Reporting Layer ]
              ├── results.csv       (De-identified summary, no raw student requests)
              ├── review_queue.csv  (Action queue for faculty, includes raw text)
              └── summary.txt       (Aggregate metrics: counts by decision, reason, course)
```

---

## 🚀 Key Features

1. **Mandatory Standalone Console Application**: Complete CLI workflow executable line-by-line via `python main.py`.
2. **Interactive Streamlit Web Dashboard**: Modern dark-themed dashboard (`streamlit run app.py`) with KPI cards, interactive Plotly distribution charts, search and course filtering, and report downloads.
3. **Five-Role Prompting Architecture**: System prompt (`system_prompt.txt`) structured around Authority, Exemplar, Constraint, Rubric, and Metadata roles.
4. **Deterministic Policy Rules**: Pure Python implementation with zero LLM overrides.
5. **Defense-in-Depth Privacy & Redaction**: Strict 15-word limit and health keyword filters preventing medical details from leaking into public summaries.
6. **Robust Cybersecurity**: Defenses against prompt injection, hallucinated date conversion, and CSV formula injection.
7. **Comprehensive Test Suite**: 26 automated `pytest` tests covering unit, integration, boundary, privacy, security, and performance benchmarks.

---

## 📂 Project Structure

```
Extension-Request-Sorter/
├── app.py                   # Streamlit interactive UI dashboard
├── main.py                  # Core console CLI application
├── extractor.py             # Groq LLM extractor, mock extractor, retry & fallback
├── validator.py             # Strict deterministic validation & privacy filters
├── policy.py                # Department extension policy rules & constants
├── reporter.py              # CSV/TXT generation & formula injection sanitizer
├── test_suite.py            # Comprehensive 26-test pytest automated test suite
├── system_prompt.txt        # Five-role prompt template
├── courses.csv              # Course registry dataset
├── requests.csv             # 22 realistic fictional test requests
├── results.csv              # Generated public report (sanitized)
├── review_queue.csv         # Generated faculty review queue (includes raw text)
├── summary.txt              # Generated aggregate metrics summary
├── SPECIFICATION.md         # One-page approved system specification
├── EVALUATION.md            # Evaluation harness benchmark results
├── RED_TEAM.md              # Adversarial attacks & security testing log
├── JUDGMENT_FRAMEWORK.md    # Cost of being wrong & governance boundary
├── COST_AND_LATENCY.md      # Latency measurements & semester cost model
├── DECISION_JOURNAL.md      # AI architectural decision logs
├── REFLECTION.md            # 400-word student engineering reflection
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
└── .gitignore               # Git secret and cache exclusion rules
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.11+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to include your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=openai/gpt-oss-120b
```
*(Note: If no API key is provided, the application automatically runs in deterministic mock mode for offline demonstration and testing).*

---

## 💻 Execution Instructions

### Run the Mandatory Console Application
```bash
python main.py
```
This reads `courses.csv` and `requests.csv`, processes all 22 requests, and generates `results.csv`, `review_queue.csv`, and `summary.txt`.

### Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to view real-time KPI metrics, upload custom files, and review flagged requests.

### Run Automated Tests
```bash
python -m pytest test_suite.py -v
```

---

## 🎓 Viva Preparation & Code Walkthrough Notes
- **`load_courses()` / `load_requests()` (`main.py`)**: Loads structured CSV data into standard Python dictionaries.
- **`classify()` (`extractor.py`)**: Submits requests to Groq API using JSON mode. Retries once upon malformed output, applying a safe fallback if validation fails twice.
- **`is_valid()` (`validator.py`)**: Verifies that extracted course codes exist in `courses.csv` and appear explicitly in the request text; confirms requested day counts are integers [1-30] explicitly written in the request; enforces 15-word privacy limits.
- **`recommend()` (`policy.py`)**: Deterministically maps verified facts into `within_policy`, `needs_faculty_review`, or `needs_more_info`.
- **`write_reports()` (`reporter.py`)**: Writes sanitized public reports while prepending single quotes to special formula characters (`=`, `+`, `-`, `@`) to block CSV formula injection attacks.
