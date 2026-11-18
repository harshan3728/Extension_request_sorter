"""
Validation and privacy sanitization module for student extension requests.
Implements strict deterministic checks to prevent hallucinated data and privacy leaks.
"""

import re
from typing import Any
from policy import VALID_REASONS

# Number words mapping from 1 to 30
WORD_TO_NUM: dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "twenty-one": 21, "twenty-two": 22, "twenty-three": 23, "twenty-four": 24,
    "twenty-five": 25, "twenty-six": 26, "twenty-seven": 27, "twenty-eight": 28,
    "twenty-nine": 29, "thirty": 30
}

# Sensitive health and personal keywords that MUST NOT appear in public summaries
PROHIBITED_HEALTH_TERMS: set[str] = {
    "infection", "dengue", "migraine", "fever", "ill", "illness", "sick", "sickness",
    "hospital", "admitted", "clinic", "doctor", "physician", "flu", "covid", "virus",
    "wrist", "broken", "fracture", "injury", "surgery", "pain", "medication", "medicine",
    "treatment", "depressed", "depression", "anxiety", "mental", "stress", "trauma",
    "grandmother", "grandfather", "mother", "father", "parent", "sister", "brother",
    "funeral", "icu"
}


def day_in_text(days: int, text: str) -> bool:
    """Checks whether the requested day integer explicitly appears in the original text."""
    lower_text = text.lower()
    
    # 1. Match as digit word boundary e.g. " 2 ", "2 days", "2-day"
    if re.search(rf"\b{days}\b", lower_text):
        return True
        
    # 2. Match as spelled-out word
    for word, val in WORD_TO_NUM.items():
        if val == days:
            pattern = rf"\b{re.escape(word)}\b"
            if re.search(pattern, lower_text):
                return True
                
    return False


def is_valid(
    data: Any,
    original_text: str,
    valid_courses: set[str]
) -> tuple[bool, str]:
    """
    Validates the extracted LLM JSON data against original text and course whitelist.
    Returns (is_valid: bool, error_reason: str).
    """
    if not isinstance(data, dict):
        return False, "Data is not a JSON object"

    # Check required keys
    expected_keys = {"course", "days", "reason", "summary"}
    if set(data.keys()) != expected_keys:
        return False, f"Keys mismatch. Expected {expected_keys}, got {set(data.keys())}"

    course = data.get("course")
    days = data.get("days")
    reason = data.get("reason")
    summary = data.get("summary")

    # Validate course
    if course is not None:
        if not isinstance(course, str):
            return False, "Course must be a string or null"
        course = course.strip().upper()
        if course not in valid_courses:
            return False, f"Course '{course}' not in valid courses whitelist"
        if not re.search(rf"\b{re.escape(course)}\b", original_text, re.IGNORECASE):
            return False, f"Course '{course}' does not explicitly appear in original request text"

    # Validate days
    if days is not None:
        if not isinstance(days, int) or isinstance(days, bool):
            return False, "Days must be an integer or null"
        if not (1 <= days <= 30):
            return False, f"Days '{days}' is out of the allowed range [1, 30]"
        if not day_in_text(days, original_text):
            return False, f"Days '{days}' does not explicitly appear in original request text"

    # Validate reason
    if reason not in VALID_REASONS:
        return False, f"Reason '{reason}' is not in valid reasons: {VALID_REASONS}"

    # Validate summary
    if not isinstance(summary, str) or not summary.strip():
        return False, "Summary must be a non-empty string"
    words = summary.strip().split()
    if len(words) > 15:
        return False, f"Summary exceeds maximum 15 words limit (got {len(words)})"

    # Privacy check on summary: No prohibited terms
    clean_summary_lower = re.sub(r"[^\w\s]", "", summary.lower())
    for word in clean_summary_lower.split():
        if word in PROHIBITED_HEALTH_TERMS:
            return False, f"Summary violates privacy constraint with prohibited term: '{word}'"

    return True, "Valid"


def generate_safe_summary(course: str | None, days: int | None, reason: str | None) -> str:
    """Generates a guaranteed neutral, privacy-compliant summary in Python."""
    c_str = course if course else "unspecified course"
    r_str = reason if reason and reason in VALID_REASONS else "other"
    if days is not None:
        return f"Requests {days} days extension for {c_str}, {r_str} reason"
    return f"Requests extension for {c_str}, {r_str} reason"
