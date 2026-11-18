# Extension Request Sorter — Cost & Latency Note
**Programme:** CIT AI-Native Engineering Programme, Semester 1  
**Assessment:** Assessment 5 — Capstone Project  
**Date:** 2026-11-17  

---

## 1. Measured Benchmarks & Empirical Latency

Performance and throughput measurements were conducted across mock and real pipeline executions:

| Batch Size | Measured Local Execution Time | Mean Latency per Request | Throughput |
|---|---|---|---|
| **20 Requests** | `2.20 ms` | `0.11 ms / req` | ~9,000 req/sec |
| **100 Requests** | `11.37 ms` | `0.11 ms / req` | ~8,800 req/sec |
| **500 Requests** | `55.68 ms` | `0.11 ms / req` | ~8,970 req/sec |

*Note: The measurements above represent the local Python validation and policy engine execution benchmarked via `pytest`.*

### Groq API Network Latency Estimates
When calling the Groq Cloud API with `openai/gpt-oss-120b`:
- **Time to First Token (TTFT):** ~120 ms – 200 ms (Groq LPU architecture).
- **Inference Speed:** ~250–350 tokens/second.
- **Total Round-Trip Latency per Request:** ~280 ms – 450 ms.
- **Estimated Batch Processing (22 Requests sequentially):** ~6.5 to 9.5 seconds.

---

## 2. API Cost Projections & Assumptions

### Cost Assumptions
- **Target Model:** `openai/gpt-oss-120b` (or equivalent open-weights hosted on Groq).
- **Current Groq Pricing Tier (Illustrative baseline):**
  - Input: \$0.59 / 1,000,000 tokens
  - Output: \$0.79 / 1,000,000 tokens
- **Per Request Token Budget:**
  - System Prompt (cached or input): ~350 tokens
  - Student Request: ~60 tokens
  - Output JSON: ~40 tokens
  - Total per request: ~410 input tokens + 40 output tokens.

### Projected Volume & Costs for CIT Department

| Operating Timeframe | Request Volume | Estimated Input Tokens | Estimated Output Tokens | Total Projected Cost |
|---|---|---|---|---|
| **Daily Batch** | 50 requests | 20,500 tokens | 2,000 tokens | **\$0.014** (approx. 1.4 cents) |
| **Peak Midterm Week** | 500 requests | 205,000 tokens | 20,000 tokens | **\$0.137** (approx. 14 cents) |
| **Full Academic Semester** | 5,000 requests | 2,050,000 tokens | 200,000 tokens | **\$1.37** (approx. \$1.37 USD) |

### Financial Viability Summary
Operating the Extension Request Sorter across an entire academic department costs less than **\$2.00 USD per semester** on Groq, delivering a massive operational return on investment by saving faculty hundreds of manual triage hours.
