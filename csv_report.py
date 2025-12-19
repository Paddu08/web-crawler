import csv
from typing import Dict, Any


def _safe_join(value) -> str:
    if isinstance(value, list):
        return ";".join(str(v) for v in value)
    return ""


def write_csv_report(
    page_data: Dict[Any, Dict[str, Any]],
    filename: str = "report.csv",
) -> None:

    fieldnames = [
        "page_url",
        "h1",
        "first_paragraph",
        "outgoing_link_urls",
        "image_urls",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for page in page_data.values():
            # 🔴 CRITICAL FIX
            if not isinstance(page, dict):
                continue

            row = {
                "page_url": page.get("url", ""),
                "h1": page.get("h1", ""),
                "first_paragraph": page.get("first_paragraph", ""),
                "outgoing_link_urls": _safe_join(page.get("outgoing_links")),
                "image_urls": _safe_join(page.get("image_urls")),
            }

            writer.writerow(row)
