import csv
import time
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
    LCSH
)
from loc_authorities.api import LocAPI
from django.db import transaction, IntegrityError

logging.basicConfig(
    filename="videoupload.log",
    format="%(asctime)s - %(message)s - %(levelname)s",
    filemode="w",
)


# converts EDTF date to datetime object
def process_date(string):
    # process year, month, and day
    ymd = string.strip().split("-")

    year = int(ymd[0])
    month = int(ymd[1])
    day = int(ymd[2])

    return datetime.datetime(year, month, day, tzinfo=ZoneInfo("America/New_York"))


def process_diglib_url(string):
    lst = string.strip().split(":")
    return lst[-1]


# splits list of AcademicDiscipline and APSDepartment on appropriate separator and retrieves database objects
# will log an error if category not found in database
def add_category_to_video(string, ModelName, separator):
    if not string:
        return
    lst = string.strip().split(separator)
    categories = []
    for item in lst:
        item_cleaned = item.strip()
        try:
            itemObj = ModelName.objects.get(name=item_cleaned)
            categories.append(itemObj)
        except:
            logging.exception(f"Category {string} not found in table {ModelName}")
            raise
    return categories


def process_affiliation(position, institution, meeting, speaker):
    affiliation, created = Affiliation.objects.get_or_create(
        position=position.strip(), institution=institution.strip(), speaker=speaker
    )
    if created:
        try:
            affiliation.full_clean()
            affiliation.save()
            print("Affiliation created for speaker: " + speaker.display_name)
        except Exception as e:
            logging.exception(
                f"Error processing affiliation {affiliation} for speaker {speaker} in meeting {meeting}: {e}"
            )
            affiliation.delete()
            raise
    # add meeting
    affiliation.meetings.add(meeting)
    return

# create LCSH and add to associated object
# can be used to associate LCSH with a video or a speaker
def create_lcsh(cell, object, field):
    # if field is empty, no LCSH need to be created
    if not cell:
        return
    
    lcsh_fields_name = ["lcsh_geographic", "lcsh_name_personal", "lcsh_name_corporate", "speaker_lcsh"]
    lcsh_fields_subject = ["lcsh_topic", "lcsh_temporal"]

    if field in lcsh_fields_name:
        authority = "names"
    elif field in lcsh_fields_subject:
        authority = "subjects"

    match field:
        case "lcsh_geographic":
            category = "GEOGRAPHIC"
        case "lcsh_name_personal":
            category = "PERSONAL_NAME"
        case "lcsh_name_corporate":
            category = "CORPORATE_NAME"
        case "speaker_lcsh":
            category = "PERSONAL_NAME"
        case "lcsh_topic":
            category = "TOPIC"
        #TODO: is this right? should it be topic?
        case "lcsh_temporal":
            category = "OTHER"
        case _:
            category = "OTHER"
    
    loc = LocAPI()

    lcsh_list = cell.strip().split("|")
    for lcsh_str in lcsh_list:
        uri = loc.retrieve_label(lcsh_str.strip(), authority=authority)
        time.sleep(1)
        if uri:
            lcsh_obj, created = LCSH.objects.get_or_create(heading=lcsh_str.strip(), uri=uri, authority="LOC")
        #special case for handling complex subject headings that can't be validated through LOC API
        # elif "--" in lcsh_str:
        #     lcsh_obj, created = LCSH.objects.get_or_create(heading=lcsh_str.strip(), authority="LOC", category="COMPLEX_SUBJECT")
        else:
            lcsh_obj, created = LCSH.objects.get_or_create(heading=lcsh_str.strip(), authority="OTHER", category=category)
            logging.exception(f"No URI found for LCSH: {lcsh_str}")

        if created:
            print(f"LCSH created: {lcsh_str}")

        # add to video
        if isinstance(object, Video):
            object.lcsh.add(lcsh_obj)
            object.save()
        elif isinstance(object, Speaker):
            object.lcsh = lcsh_obj
            object.label = lcsh_obj.heading
            object.save()
        else:
            print("Object passed to create_lcsh was not a speaker or video. Did you associate your LCSH with the correct thing?")
            #TODO: is this necessary? change to logging?
        

# create speaker object and add to video
# only process display name and affiliation - speaker LCSH will be handled with other LCSH
def add_speaker_to_video(
    video,
    display_name,
    position_1,
    institution_1,
    position_2,
    institution_2,
    meeting,
    label
):
    # CREATE SPEAKER LCSH FIRST
    # pass LCSH as a list

    speaker, created = Speaker.objects.get_or_create(
        display_name=display_name.strip(), label=label.strip()
    )

    if created:
        try:
            speaker.full_clean()
            speaker.save()

            create_lcsh(label, speaker, "speaker_lcsh")
        except Exception as e:
            logging.exception(
                f"Error saving speaker {speaker} for video {video} in meeting {meeting}: {e}"
            )
            speaker.delete()
            raise

    video.speakers.add(speaker)
    print("Speaker added: " + speaker.display_name)

    # if affiliation, create new affiliation
    if position_1 or institution_1:
        process_affiliation(position_1, institution_1, meeting, speaker)
    if position_2 or institution_2:
        process_affiliation(position_2, institution_2, meeting, speaker)


def process_symposium(title, meeting, date):
    if title:
        symposium, created = Symposium.objects.get_or_create(
            title=title.strip(), meeting=meeting, date=date
        )
        if created:
            try:
                symposium.full_clean()
                symposium.save()
                print("Symposium added: " + symposium.title)
            except Exception as e:
                logging.exception(f"Error saving symposium {symposium} for meeting {meeting}: {e}")
                symposium.delete()
                raise
        return symposium

    return None


# process individual spreadsheet row to create video
def process_video(row):
    print("\n-----------\nVIDEO: " + row["title"] + "\n")

    # find correct meeting - search by name
    meeting = Meeting.objects.get(display_date=row["meeting"])

    # create date object
    date = process_date(row["date"])

    # find or create symposium
    symposium = process_symposium(row["symposium"], meeting, date)

    # TODO: let this update video object if not all data matches? which fields should ID it?
    video, created = Video.objects.get_or_create(
        title=row["title"].strip(),
        lecture_additional_info=row["lecture_additional_info"].strip(),
        abstract=row["abstract"].strip(),
        doi=row["proceedings_url"].strip(),
        proceedings_title=row["proceedings_title"].strip(),
        service_file=row["service_file"].strip(),
        youtube_url=row["youtube_url"].strip(),
        display_notes=row["display_notes"].strip(),
        admin_notes=row["admin_notes"].strip(),
        node=row["node"].strip(),
        admin_category=row["admin_category"].strip(),
        meeting=meeting,
        symposium=symposium,
        date=date,
        order_in_day=row["order_in_day"].strip(),
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
        except Exception as e:
            logging.exception(
                f"Video {video} in meeting {meeting}: Exception occurred: {str(e)}"
            )
            video.delete()
            raise

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

        # add lcsh
        # do for lcsh_topic, lcsh_geographic, lcsh_temporal, lcsh_name_personal
        # need to split for all of these
        # print to log if not valid
        lcsh_fields = ["lcsh_geographic", "lcsh_name_personal", "lcsh_name_corporate", "lcsh_topic", "lcsh_temporal"]

        for field in lcsh_fields:
            create_lcsh(row[field], video, field)

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
            row["speaker_lcsh"],
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
            row["speaker_2_lcsh"],
        )


# loop through spreadsheet, adding a video for each row
def upload_videos():
    with open("videos-new.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                with transaction.atomic():
                    process_video(row)
            except Exception as e:
                logging.exception(f"Error saving video {row['title']} in meeting {row['meeting']}: {e}")
