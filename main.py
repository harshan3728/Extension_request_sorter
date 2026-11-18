"""
Extension Request Sorter — Core Console Application.
Processes student requests using LLM extraction and deterministic Python policy rules.
Generates results.csv, review_queue.csv, and summary.txt.
"""

import os
import sys
import csv
from typing import Any
from dotenv import load_dotenv

# Local modules
from extractor import classify, load_system_prompt, DEFAULT_MODEL
from validator import is_valid
from policy import recommend
from reporter import write_reports


def load_courses(courses_path: str = "courses.csv") -> dict[str, str]:
    """
    Reads courses.csv and returns a mapping of course_code -> course_name.
    """
    if not os.path.exists(courses_path):
        raise FileNotFoundError(f"Courses file not found: {courses_path}")

    courses: dict[str, str] = {}
    with open(courses_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("code", "").strip().upper()
            name = row.get("name", "").strip()
            if code:
                courses[code] = name
    return courses


def load_requests(requests_path: str = "requests.csv") -> list[dict[str, str]]:
    """
    Reads requests.csv and returns a list of request dictionaries (id, date, request).
    """
    if not os.path.exists(requests_path):
        raise FileNotFoundError(f"Requests file not found: {requests_path}")

    requests: list[dict[str, str]] = []
    with open(requests_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            req_id = row.get("id", "").strip()
            date = row.get("date", "").strip()
            text = row.get("request", "").strip()
            if req_id:
                requests.append({
                    "id": req_id,
                    "date": date,
                    "request": text
                })
    return requests


def process_all_requests(
    requests_path: str = "requests.csv",
    courses_path: str = "courses.csv",
    results_path: str = "results.csv",
    review_queue_path: str = "review_queue.csv",
    summary_path: str = "summary.txt"
) -> list[dict[str, Any]]:
    """
    Main processing orchestration: loads inputs, runs extraction, validates,
    applies policy, and writes all reports.
    """
    load_dotenv()

    courses = load_courses(courses_path)
    valid_courses = set(courses.keys())
    requests_list = load_requests(requests_path)
    system_prompt = load_system_prompt()

    print("\n" + "=" * 65)
    print("      CIT EXTENSION REQUEST SORTER — CONSOLE ENGINE")
    print("=" * 65)
    print(f"Loaded {len(courses)} active courses.")
    print(f"Loaded {len(requests_list)} student requests to process.\n")

    processed_records: list[dict[str, Any]] = []

    for idx, item in enumerate(requests_list, start=1):
        req_id = item["id"]
        req_date = item["date"]
        raw_text = item["request"]

        # Step 1: Classify / Extract
        extracted = classify(raw_text, valid_courses, system_prompt=system_prompt)

        # Step 2: Validate
        valid, msg = is_valid(extracted, raw_text, valid_courses)
        if not valid:
            course = None
            days = None
            reason = "other"
            summary = "Validation error: details unverified"
        else:
            course = extracted.get("course")
            days = extracted.get("days")
            reason = extracted.get("reason")
            summary = extracted.get("summary")

        # Step 3: Deterministic Policy Recommendation
        status = recommend(course, days, reason)

        record = {
            "id": req_id,
            "date": req_date,
            "course": course,
            "days": days,
            "reason": reason,
            "recommendation": status,
            "summary": summary,
            "request": raw_text  # Kept in memory only for review_queue.csv
        }
        processed_records.append(record)

        print(f"[{idx:02d}/{len(requests_list):02d}] {req_id} | Course: {str(course):<6} | Days: {str(days):<4} | Reason: {str(reason):<10} -> {status}")

    # Step 4: Write output reports
    write_reports(
        processed_records,
        results_path=results_path,
        review_queue_path=review_queue_path,
        summary_path=summary_path
    )

    print("\n" + "=" * 65)
    print(f"Successfully wrote reports:")
    print(f" - Results (public safe) : {results_path}")
    print(f" - Review Queue (faculty): {review_queue_path}")
    print(f" - Summary (metrics)     : {summary_path}")
    print("=" * 65 + "\n")

    return processed_records


def main() -> None:
    """Console entrypoint."""
    try:
        process_all_requests()
    except Exception as e:
        print(f"\n[ERROR] Process failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
