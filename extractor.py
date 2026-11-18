"""
Information extraction module interfacing with the Groq API.
Handles five-role system prompt loading, structured JSON extraction,
one retry attempt on validation failure, and deterministic safe fallback.
"""

import os
import json
import re
from typing import Any
from validator import is_valid, generate_safe_summary, WORD_TO_NUM
from policy import VALID_REASONS

DEFAULT_MODEL = "openai/gpt-oss-120b"


def load_system_prompt(path: str = "system_prompt.txt") -> str:
    """Loads the 5-role system prompt from file."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are the CIT Academic Registry Information Extractor. Return JSON with course, days, reason, summary."


def mock_classify(
    request_text: str,
    valid_courses: set[str]
) -> dict[str, Any]:
    """
    Deterministic rule-based extractor used during offline testing or when GROQ_API_KEY is not set.
    Performs conservative extraction matching the exact system prompt rules.
    """
    # 1. Course extraction
    course = None
    for c in sorted(valid_courses, key=len, reverse=True):
        if re.search(rf"\b{re.escape(c)}\b", request_text, re.IGNORECASE):
            course = c
            break

    # 2. Days extraction (explicit digits or spelled out, strictly 1-30)
    days = None
    # Check digits
    digit_matches = re.findall(r"\b(\d+)\s*(?:days?|day)?\b", request_text, re.IGNORECASE)
    # Check spelled out words
    word_matches = []
    lower_text = request_text.lower()
    for word, val in WORD_TO_NUM.items():
        if re.search(rf"\b{re.escape(word)}\s*(?:days?|day)?\b", lower_text):
            word_matches.append((val, word))

    # Guard: Avoid interpreting dates (e.g., 2026-11-08) or large hours as days
    # Prioritize numbers adjacent to "day" or "days"
    day_specific_match = re.search(r"\b(\d+)\s*[-]?\s*days?\b", request_text, re.IGNORECASE)
    word_specific_match = None
    for word, val in WORD_TO_NUM.items():
        if re.search(rf"\b{re.escape(word)}\s*[-]?\s*days?\b", lower_text):
            word_specific_match = val
            break

    if day_specific_match:
        val = int(day_specific_match.group(1))
        if 1 <= val <= 30:
            days = val
    elif word_specific_match:
        days = word_specific_match
    elif digit_matches:
        for dm in digit_matches:
            val = int(dm)
            if 1 <= val <= 30 and f"-{val}" not in request_text and f"{val}-" not in request_text:
                days = val
                break
    elif word_matches:
        days = word_matches[0][0]

    # 3. Reason classification
    reason = "other"
    if re.search(r"\b(infection|clinic|unwell|hospital|fever|wrist|migraine|sick|medical|health)\b", lower_text):
        reason = "medical"
    elif re.search(r"\b(family|hometown|wedding|emergency|grandmother)\b", lower_text):
        reason = "family"
    elif re.search(r"\b(battery|laptop|charger|internet|wifi|router|desktop|water|flooded|technical|lightning)\b", lower_text):
        reason = "technical"
    elif re.search(r"\b(fest|cultural|sports|event|competition)\b", lower_text):
        reason = "event"
    elif re.search(r"\b(midterms|deadlines|workload|colliding|stress)\b", lower_text):
        reason = "workload"

    # 4. Privacy-compliant summary
    summary = generate_safe_summary(course, days, reason)

    return {
        "course": course,
        "days": days,
        "reason": reason,
        "summary": summary
    }


def call_groq_api(
    client: Any,
    model: str,
    system_prompt: str,
    request_text: str
) -> dict[str, Any]:
    """Sends a completion request to Groq API and parses JSON output."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Student Request:\n\"\"\"{request_text}\"\"\""}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    content = response.choices[0].message.content.strip()
    return json.loads(content)


def classify(
    request_text: str,
    valid_courses: set[str],
    system_prompt: str | None = None,
    client: Any = None,
    model: str | None = None
) -> dict[str, Any]:
    """
    Classifies a student request using Groq LLM (or mock fallback if unconfigured).
    Includes 1 retry on validation failure, and safe fallback.
    """
    if system_prompt is None:
        system_prompt = load_system_prompt()

    active_model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)

    # If client is None or API key not present, use mock_classify
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and api_key != "your_key_here":
            try:
                from groq import Groq
                client = Groq(api_key=api_key)
            except Exception:
                client = None

    if client is None:
        raw_data = mock_classify(request_text, valid_courses)
        valid, msg = is_valid(raw_data, request_text, valid_courses)
        if valid:
            return raw_data
        # Fallback
        return {
            "course": None,
            "days": None,
            "reason": "other",
            "summary": "Processing fallback: Unverified request details"
        }

    # Attempt 1
    for attempt in range(2):
        try:
            raw_data = call_groq_api(client, active_model, system_prompt, request_text)
            valid, reason_msg = is_valid(raw_data, request_text, valid_courses)
            if valid:
                return raw_data
        except Exception:
            pass  # Retry on exception or validation error

    # Safe fallback if both attempts fail
    return {
        "course": None,
        "days": None,
        "reason": "other",
        "summary": "Safe fallback: AI extraction failed validation"
    }
