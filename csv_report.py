import csv


def write_csv_report(page_data, filename="report.csv"):
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
            writer.writerow(page)
