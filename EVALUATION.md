# Extension Request Sorter — Evaluation Harness & Benchmark Results
**Programme:** CIT AI-Native Engineering Programme, Semester 1  
**Assessment:** Assessment 5 — Capstone Project  
**Date:** 2026-11-17  

---

## 1. Evaluation Dataset & Labeled Ground Truth

We evaluated the Extension Request Sorter on 5 diverse benchmark requests representing distinct edge cases and conditions:

| ID | Input Request Text | Expected Course | Expected Days | Expected Reason | Expected Recommendation |
|---|---|---|---|---|---|
| **EVAL-01** | "Dear Professor, I came down with a severe stomach infection and visited clinic yesterday. Need 2 days extension for CS101." | `CS101` | `2` | `medical` | `within_policy` |
| **EVAL-02** | "Hi Professor, I have been admitted to hospital with dengue fever and need 10 days extension for MA102 problem set." | `MA102` | `10` | `medical` | `needs_faculty_review` |
| **EVAL-03** | "Dear Instructor, I am participating as an organizer in the CIT Inter-Collegiate Cultural Fest this weekend. Can I get a 3 day extension for CS101?" | `CS101` | `3` | `event` | `needs_faculty_review` |
| **EVAL-04** | "Respected Sir, my Wi-Fi router was struck by lightning yesterday during rain. May I have 1 day extension for MA102 assignment 4?" | `MA102` | `1` | `technical` | `within_policy` |
| **EVAL-05** | "Dear Sir, I am unwell and need 2 days extension for my assignment. Thank you." | `null` | `2` | `medical` | `needs_more_info` |

---

## 2. Evaluation Execution Results

| ID | Extracted Course | Extracted Days | Extracted Reason | Generated Recommendation | Status | Result Match |
|---|---|---|---|---|---|---|
| **EVAL-01** | `CS101` | `2` | `medical` | `within_policy` | ✅ PASS | Exact Match |
| **EVAL-02** | `MA102` | `10` | `medical` | `needs_faculty_review` | ✅ PASS | Exact Match |
| **EVAL-03** | `CS101` | `3` | `event` | `needs_faculty_review` | ✅ PASS | Exact Match |
| **EVAL-04** | `MA102` | `1` | `technical` | `within_policy` | ✅ PASS | Exact Match |
| **EVAL-05** | `null` | `2` | `medical` | `needs_more_info` | ✅ PASS | Exact Match |

### Summary Statistics
- **Total Test Cases:** 5
- **Correct Extractions:** 5 / 5 (100%)
- **Correct Policy Recommendations:** 5 / 5 (100%)
- **Privacy Violations in Summaries:** 0 / 5 (0%)
- **Overall Accuracy:** **100%**
