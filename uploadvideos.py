import csv
import datetime
import logging
from zoneinfo import ZoneInfo
from meetingsvideos.models import (
    Meeting,
    Video,
    AcademicDiscipline,
    APSDepartment,
    Symposium,
    Speaker,
    Affiliation,
)

logging.basicConfig(filename="videoupload.log",
                    format='%(asctime)s - %(message)s - %(levelname)s',
                    filemode='w')


# converts EDTF date to datetime object
def process_date(string):
    # process year, month, and day
    ymd = string.split("-")

    year = int(ymd[0])
    month = int(ymd[1])
    day = int(ymd[2])

    return datetime.datetime(year, month, day, tzinfo=ZoneInfo("America/New_York"))



def process_diglib_url(string):
    lst = string.split(":")
    return lst[-1]


# splits list of AcademicDiscipline and APSDepartment on appropriate separator and retrieves database objects
# will log an error if category not found in database
def add_category_to_video(string, ModelName, separator):
    if not string:
        return
    lst = string.split(separator)
    categories = []
    for item in lst:
        item_cleaned = item.strip()
        try:
            itemObj = ModelName.objects.get(name=item_cleaned)
            categories.append(itemObj)
        except:
            logging.exception(f"Category {string} not found in table {ModelName}")
    return categories


def process_affiliation(position, institution, meeting, speaker):
    affiliation, created = Affiliation.objects.get_or_create(
        meeting=meeting, position=position, institution=institution, speaker=speaker
    )
    if created:
        try:
            affiliation.full_clean()
            affiliation.save()
            print("Affiliation created for speaker: " + speaker.display_name)
        except:
            logging.exception(f"Affiliation {affiliation} for speaker {speaker} in meeting {meeting}")
            affiliation.delete()
    return


# create speaker object and add to video
# only process display name and affiliation - speaker LCSH will be handled with other LCSH
def add_speaker_to_video(
    video, display_name, position_1, institution_1, position_2, institution_2, meeting
):
    speaker, created = Speaker.objects.get_or_create(display_name=display_name)

    if created:
        try:
            speaker.full_clean()
            speaker.save()
        except:
            logging.exception(f"Speaker {speaker} for video {video} in meeting {meeting}")
            speaker.delete()
            return
            
    video.speakers.add(speaker)
    print("Speaker added: " + speaker.display_name)
    
    # if affiliation, create new affiliation
    if position_1 or institution_1:
        process_affiliation(position_1, institution_1, meeting, speaker)
    if position_2 or institution_2:
        process_affiliation(position_2, institution_2, meeting, speaker)


def process_symposium(str, meeting):
    if str:
        symposium, created = Symposium.objects.get_or_create(title=str, meeting=meeting)
        if created:
            try:
                symposium.full_clean()
                symposium.save()
                print("Symposium added: " + symposium.title)
            except:
                logging.exception(f"Symposium {symposium} for meeting {meeting}")
                symposium.delete()
                return None
        return symposium

    return None


# process individual spreadsheet row to create video
def process_video(row):
    print("\n-----------\nVIDEO: " + row["title"] + "\n")

    # find correct meeting - search by name
    meeting = Meeting.objects.get(display_date=row["meeting"])

    # find or create symposium
    symposium = process_symposium(row["symposium"], meeting)
    
    # create date object
    date=process_date(row["date"])

    # TODO: let this update video object if not all data matches? which fields should ID it?
    video, created = Video.objects.get_or_create(
        title=row["title"],
        lecture_additional_info=row["lecture_additional_info"],
        abstract=row["abstract"],
        doi=row["doi"],
        service_file=row["service_file"],
        youtube_url=row["youtube_url"],
        display_notes=row["display_notes"],
        admin_notes=row["admin_notes"],
        diglib_pid=row["pid"].replace("video:", ""),
        admin_category=row["admin_category"],
        meeting=meeting,
        symposium=symposium,
        date=date,
        order_in_day=row["order_in_day"],
    )

    # if record for this video already exists, alert user
    if not created:
        print("Video already exists in database; no new record created")
    # if record is new, add remaining details
    else:
        try:
            video.full_clean()
            video.save()
            print("Video created: " + video.title)
        except:
            logging.exception(f"Video {video} in meeting {meeting}: Exception occurred: {str(e)}")
            video.delete()
            return

        # add department and discipline
        departments = add_category_to_video(row["aps_departments"], APSDepartment, ",")
        if departments:
            for department in departments:
                video.aps_departments.add(department)

        disciplines = add_category_to_video(
            row["academic_disciplines"], AcademicDiscipline, "|"
        )
        if disciplines:
            for discipline in disciplines:
                video.academic_disciplines.add(discipline)
        
    # add speaker info
    # this will run regardless of whether a new video has been created or not, in order to allow adding more than two speakers to a video by creating an additional row for that video
    if row["speaker_lcsh"]:
        add_speaker_to_video(
            video,
            row["speaker_display_name"],
            row["speaker_position"],
            row["speaker_institution"],
            row["speaker_position_2"],
            row["speaker_institution_2"],
            meeting,
        )

    if row["speaker_2_lcsh"]:
        add_speaker_to_video(
            video,
            row["speaker_2_display_name"],
            row["speaker_2_position"],
            row["speaker_2_institution"],
            row["speaker_2_position_2"],
            row["speaker_2_institution_2"],
            meeting,
        )


# loop through spreadsheet, adding a video for each row
def upload_videos():
    with open("videos-duplicate.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                process_video(row)
            except:
                logging.exception(f"Video {row["title"]} in meeting {row["meeting"]}")