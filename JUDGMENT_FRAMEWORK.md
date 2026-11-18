# Extension Request Sorter — Judgment Framework
**Programme:** CIT AI-Native Engineering Programme, Semester 1  
**Assessment:** Assessment 5 — Capstone Project  
**Date:** 2026-11-17  

---

## 1. Governance & Decision Boundary Framework

The Judgment Framework defines which system elements are handled by AI, which are enforced by deterministic code, and which must remain under human governance.

| System Decision / Task | Handled By | Cost of Being Wrong | Can Python Verify Without AI? | Accountable Authority |
|---|---|---|---|---|
| **Fact Extraction: Course Code** | Groq LLM (`openai/gpt-oss-120b`) | Moderate (Student request tagged to wrong course) | **YES** (Regex string search against `courses.csv`) | Python Validator Layer |
| **Fact Extraction: Requested Days** | Groq LLM (`openai/gpt-oss-120b`) | High (Unauthorized days granted or truncated) | **YES** (Integer presence & range [1-30] verification in original text) | Python Validator Layer |
| **Reason Classification** | Groq LLM (`openai/gpt-oss-120b`) | Moderate to High (Wrong policy route triggered) | **NO** (Semantic understanding required across infinite phrasings) | Course Faculty Review |
| **Genuineness of Claim** | Human / Faculty | Very High (Academic dishonesty or unfair penalty) | **NO** (Cannot verify if illness or emergency actually occurred) | Course Faculty & Academic Board |
| **Policy Recommendation** | Deterministic Python Engine | Critical (Unfair treatment or policy breach) | **YES** (Deterministic `if/else` execution) | Software Engineer & Department Policy |
| **Final Approval / Rejection** | Course Faculty | Critical (Legal, academic, and degree implications) | **NO** (Sole legal responsibility of academic faculty) | Course Faculty & Academic Registry |

---

## 2. Inherent AI Limitations & Human-in-the-Loop Safeguards

### Why Python Cannot Reliably Verify Claims Without Human Oversight
While Python regex and deterministic algorithms easily verify syntax (such as whether `"CS101"` appears in the text or whether `"2"` is between 1 and 30), **Python cannot determine the authenticity or truth of a student's personal circumstances**. 

1. **Semantic Nuance & Ambiguity**: A student stating *"my grandfather passed away"* vs *"I attended a family event"* requires semantic categorization that deterministic scripts cannot generalize across novel formulations.
2. **Medical Authenticity**: Neither an LLM nor a Python script can inspect medical certificates, clinic slips, or hospital records. 
3. **Equitable Fairness**: Unforeseen compassionate grounds (e.g. bereavement, natural disasters) require faculty empathy and human discretion that AI must never possess.

### Structural Safeguard: System Never Approves or Rejects
To guarantee student welfare and academic integrity:
- The system **only sorts requests into recommendations** (`within_policy`, `needs_faculty_review`, `needs_more_info`).
- The system **never outputs approval or rejection notices**.
- All non-standard requests are queued directly in `review_queue.csv` for human faculty review with the full original context preserved.
