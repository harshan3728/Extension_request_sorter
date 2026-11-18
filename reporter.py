"""
Reports and CSV generation module for Extension Request Sorter.
Ensures privacy compliance and CSV injection prevention.
"""

import csv
import io
from typing import Any


def sanitize_csv_value(val: Any) -> str:
    """
    Prevents CSV formula injection by prepending a single quote if the value
    starts with dangerous symbols (=, +, -, @, tab, CR).
    """
    if val is None:
        return ""
    s = str(val)
    if s.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + s
    return s


def write_reports(
    records: list[dict[str, Any]],
    results_path: str = "results.csv",
    review_queue_path: str = "review_queue.csv",
    summary_path: str = "summary.txt"
) -> None:
    """
    Writes results.csv, review_queue.csv, and summary.txt.

    Privacy Rules:
    - results.csv NEVER contains original student request text.
    - review_queue.csv contains requests that are NOT 'within_policy', and includes original text for faculty review.
    - summary.txt contains aggregated metrics only; no student requests.
    """
    # 1. Write results.csv
    results_fields = ["id", "date", "course", "days", "reason", "recommendation", "summary"]
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(results_fields)
        for r in records:
            writer.writerow([
                sanitize_csv_value(r.get("id")),
                sanitize_csv_value(r.get("date")),
                sanitize_csv_value(r.get("course") or ""),
                sanitize_csv_value(r.get("days") if r.get("days") is not None else ""),
                sanitize_csv_value(r.get("reason") or "other"),
                sanitize_csv_value(r.get("recommendation")),
                sanitize_csv_value(r.get("summary") or "")
            ])

    # 2. Write review_queue.csv
    review_fields = ["id", "date", "course", "days", "reason", "recommendation", "summary", "request"]
    with open(review_queue_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(review_fields)
        for r in records:
            if r.get("recommendation") != "within_policy":
                writer.writerow([
                    sanitize_csv_value(r.get("id")),
                    sanitize_csv_value(r.get("date")),
                    sanitize_csv_value(r.get("course") or ""),
                    sanitize_csv_value(r.get("days") if r.get("days") is not None else ""),
                    sanitize_csv_value(r.get("reason") or "other"),
                    sanitize_csv_value(r.get("recommendation")),
                    sanitize_csv_value(r.get("summary") or ""),
                    sanitize_csv_value(r.get("request") or "")
                ])

    # 3. Aggregate statistics for summary.txt
    total = len(records)
    rec_counts: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    course_counts: dict[str, int] = {}

    for r in records:
        rec = r.get("recommendation", "unknown")
        rec_counts[rec] = rec_counts.get(rec, 0) + 1

        reason = r.get("reason") or "other"
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

        course = r.get("course") or "Unspecified"
        course_counts[course] = course_counts.get(course, 0) + 1

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("      EXTENSION REQUEST SORTER — PROCESSING SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Requests Processed: {total}\n\n")

        f.write("-" * 40 + "\n")
        f.write("Recommendations Breakdown:\n")
        f.write("-" * 40 + "\n")
        for rec, count in sorted(rec_counts.items()):
            f.write(f"  - {rec:<25}: {count}\n")
        f.write("\n")

        f.write("-" * 40 + "\n")
        f.write("Reasons Breakdown:\n")
        f.write("-" * 40 + "\n")
        for reason, count in sorted(reason_counts.items()):
            f.write(f"  - {reason:<25}: {count}\n")
        f.write("\n")

        f.write("-" * 40 + "\n")
        f.write("Courses Breakdown:\n")
        f.write("-" * 40 + "\n")
        for course, count in sorted(course_counts.items()):
            f.write(f"  - {course:<25}: {count}\n")
        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write("Note: This summary is de-identified and safe for public or administrative distribution.\n")
