"""
Core business policy for assignment extension sorting.
Policy rules are deterministic and implemented exclusively in Python.
The system NEVER approves or rejects requests; it assigns policy recommendation statuses.
"""

# Configurable constants
MAX_DAYS_WITHIN_POLICY: int = 3

ELIGIBLE_REASONS: set[str] = {
    "medical",
    "family",
    "technical"
}

VALID_REASONS: set[str] = {
    "medical",
    "family",
    "technical",
    "event",
    "workload",
    "other"
}

STATUS_WITHIN_POLICY = "within_policy"
STATUS_NEEDS_MORE_INFO = "needs_more_info"
STATUS_NEEDS_FACULTY_REVIEW = "needs_faculty_review"


def recommend(course: str | None, days: int | None, reason: str | None) -> str:
    """
    Evaluates verified extracted facts and returns a deterministic policy recommendation.

    Policy rules:
    - Rule 1: If course or days is missing (None or empty) -> 'needs_more_info'
    - Rule 2: If days <= 3 and reason is in ELIGIBLE_REASONS -> 'within_policy'
    - Rule 3: All other cases -> 'needs_faculty_review'
    """
    # Rule 1: Missing core required fields
    if course is None or str(course).strip() == "" or days is None:
        return STATUS_NEEDS_MORE_INFO

    # Normalize reason
    clean_reason = str(reason).strip().lower() if reason else "other"

    # Rule 2: Within policy
    if 1 <= days <= MAX_DAYS_WITHIN_POLICY and clean_reason in ELIGIBLE_REASONS:
        return STATUS_WITHIN_POLICY

    # Rule 3: All other cases need faculty review
    return STATUS_NEEDS_FACULTY_REVIEW
