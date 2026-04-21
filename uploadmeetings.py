import csv
from datetime import date
from meetingsvideos.models import Meeting
import logging
from django.db import transaction


logging.getLogger(__name__)

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
            try:
                with transaction.atomic():
                    # meetings.csv now contains records with program nodes but no videos or other data - skip these for now
                    if not row["start_date"]:
                        continue
                    
                    meeting, created = Meeting.objects.get_or_create(
                        display_date=row["display_date"],
                        start_date=process_date(row["start_date"]),
                        end_date=process_date(row["end_date"]),
                        url=row["url"],
                        display_notes=row["display_notes"],
                        admin_notes=row["admin_notes"],
                    )
                    
                    if row["program_node"]:
                        meeting.program_node = row["program_node"]
                    meeting.save()
                    print(f"Meeting created: {row['display_date']}")
                    # print(process_date(row['start_date']))
            except Exception as e:
                logging.exception(f"Error creating meeting: {row['display_date']}")
