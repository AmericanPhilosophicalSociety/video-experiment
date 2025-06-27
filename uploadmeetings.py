# this is the process used to upload data from csv via the Django shell
# unsure how it will work as a script
import csv
from datetime import date
from meetingsvideos.models import Meeting

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# import django
# django.setup()

# from django.core.management import call_command


def process_date(str):
    lst = str.split("-")

    year = int(lst[0])
    month = int(lst[1])
    day = int(lst[2])

    return date(year, month, day)


def load_csv():
    with open("meetings.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            meeting = Meeting(
                display_date=row["display_date"],
                start_date=process_date(row["start_date"]),
                end_date=process_date(row["end_date"]),
                url=row["url"],
                display_notes=row["display_notes"],
                admin_notes=row["admin_notes"],
            )
            meeting.save()
            # print(row['display_date'])
            # print(process_date(row['start_date']))
