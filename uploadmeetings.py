import csv
from datetime import date
from meetingsvideos.models import Meeting


def process_date(str):
    lst = str.split("-")

    year = int(lst[0])
    month = int(lst[1])
    day = int(lst[2])

    return date(year, month, day)


def upload_meetings():
    with open("meetings.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            meeting, created = Meeting.objects.get_or_create(
                display_date=row["display_date"],
                start_date=process_date(row["start_date"]),
                end_date=process_date(row["end_date"]),
                url=row["url"],
                display_notes=row["display_notes"],
                admin_notes=row["admin_notes"],
            )
            # print(row['display_date'])
            # print(process_date(row['start_date']))
