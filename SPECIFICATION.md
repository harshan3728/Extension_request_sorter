# Extension Request Sorter — One-Page System Specification
**Programme:** CIT AI-Native Engineering Programme, Semester 1  
**Assessment:** Assessment 5 — Capstone Project  
**Domain:** Higher Education Administration  
**Project Folder:** `Extension-Request-Sorter`  
**Version:** 1.0 (Draft for Faculty Sign-off)  
**Date:** 2026-11-17  

---

## 1. System Purpose & Operational Boundary
The **Extension Request Sorter** processes incoming unstructured student assignment-extension requests. It employs a Large Language Model (Groq API, `openai/gpt-oss-120b`) strictly for **information extraction and summarization**, paired with a **deterministic Python policy engine** for recommendation sorting.

> **CRITICAL DECISION RULE:** The system **never approves or rejects** an extension request. All final determinations remain the sole legal and academic responsibility of course faculty and academic registry officers.

---

## 2. Core Architecture & Workflow
```
[ student requests.csv ] + [ courses.csv ]
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

## 3. Technology Stack & Configuration
* **Runtime:** Python 3.11+
* **LLM Engine:** Groq API (`openai/gpt-oss-120b`, configurable via `GROQ_MODEL`)
* **SDKs & Libraries:** `groq`, `streamlit`, `pandas`, `pytest`, `python-dotenv`, standard library `csv`, `json`, `re`
* **Interfaces:**
  1. **Mandatory CLI:** Standalone console application executable line-by-line (`python main.py`).
  2. **Faculty Dashboard:** Modern dark-themed Streamlit UI (`streamlit run app.py`).

---

## 4. Policy Rules & Constants
Implemented strictly in pure Python without LLM overrides:
```python
MAX_DAYS_WITHIN_POLICY = 3
ELIGIBLE_REASONS = {"medical", "family", "technical"}
# Ineligible or complex categories: "event", "workload", "other"
```
* **`within_policy`**: Explicit valid course, days between 1 and 3, reason in `ELIGIBLE_REASONS`.
* **`needs_more_info`**: Missing/unverified course code or missing/unverified day count.
* **`needs_faculty_review`**: Days > 3 (up to 30), reasons outside eligible list (event, workload, other), or edge conditions.

---

## 5. Privacy, Redaction & Security Controls
* **Student Privacy Safeguard:** Generated summaries must never exceed 15 words and must not contain student names, specific illness/diagnosis names (e.g., flu, migraine, depression), or treatments/medications.
* **File Separation:** `results.csv` and `summary.txt` contain strictly sanitized records and neutral summaries. Only `review_queue.csv` retains the raw request text for authorized faculty evaluation.
* **Prompt Injection Resilience:** System prompt contains explicit instructions ignoring embedded student directives (e.g., "approve this immediately"). Python validation rejects days/courses not explicitly matching the input request.

---

## 6. Required Deliverables & Verification Plan
1. **Input Datasets:** `courses.csv` (course registry) & `requests.csv` (20+ realistic test cases).
2. **Prompts & Logic:** `system_prompt.txt` (5-role framework), modular core modules (`extractor.py`, `validator.py`, `policy.py`, `reporter.py`).
3. **Automated Test Suite:** Comprehensive `pytest` test suite covering unit, integration, boundary, privacy, and red-team/security test vectors.
4. **Interactive Dashboard:** Streamlit application providing real-time triage, search/filter, and export controls.
5. **Academic Artifacts:** Evaluation report, Red-Team log, Judgment Framework, Decision Journal, and student reflection.

---
**Faculty Sign-Off Status:** `[ PENDING FACULTY APPROVAL ]`
