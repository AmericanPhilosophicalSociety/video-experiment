import csv
import datetime
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


# converts EDTF date to datetime object
def process_time(str):
    lst = str.split("T")

    # process year, month, and day
    ymd = lst[0].split("-")

    year = int(ymd[0])
    month = int(ymd[1])
    day = int(ymd[2])

    # date_obj = date(year, month, day)

    # process time
    hms = lst[1].split(":")
    hour = int(hms[0])
    minute = int(hms[1])

    # time_obj = time(hour, minute)

    return datetime.datetime(
        year, month, day, hour, minute, tzinfo=ZoneInfo("America/New_York")
    )


def process_diglib_url(str):
    lst = str.split(":")
    return lst[-1]


# TODO: does this work? print error if category doesn't exist
# split list of categories on | and add to appropriate field in Video
# will throw an error if category does not already exist in database
def add_category_to_video(str, ModelName):
    if not str:
        return
    lst = str.split("|")
    categories = []
    for item in lst:
        itemObj = ModelName.objects.get(name=item)
        categories.append(itemObj)
    return categories


def process_affiliation(position, institution, meeting, speaker):
    affiliation, created = Affiliation.objects.get_or_create(
        meeting=meeting, position=position, institution=institution, speaker=speaker
    )
    if created:
        affiliation.save()
        print("Affiliation created for speaker: " + speaker.display_name)
    return


# create speaker object and add to video
# only process display name and affiliation - LCSH will be handled with other LCSH
def add_speaker_to_video(video, display_name, position_1, institution_1, position_2, institution_2, meeting):
    speaker, created = Speaker.objects.get_or_create(
            display_name=display_name
        )

    if created:
        speaker.save()
        print("Speaker added: " + speaker.display_name)

    # if affiliation, create new affiliation
    if position_1 or institution_1:
        process_affiliation(position_1, institution_1, meeting, speaker)
    if position_2 or institution_2:
        process_affiliation(position_2, institution_2, meeting, speaker)
        print("if position_2 or institution_2 runs")
    video.speakers.add(speaker)


def process_symposium(str, meeting):
    reminders = ""
    if str:
        symposium, created = Symposium.objects.get_or_create(title=str, meeting=meeting)
        if created:
            print("Symposium added: " + symposium.title)
            reminders += (
                "**ADD MODERATOR INFO for the following symposium: " + str + "\n"
            )

        return symposium, reminders
    else:
        return None, reminders


# process individual spreadsheet row to create video
def process_video(row):
    print("\n-----------\nVIDEO: " + row["title"] + "\n")

    # find correct meeting - search by name
    meeting = Meeting.objects.get(display_date=row["meeting"])

    # find or create symposium
    symposium, reminders = process_symposium(row["symposium"], meeting)

    # create date and time
    time_obj = process_time(row["time"])

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
        diglib_pid=process_diglib_url(row["diglib_url"]),
        admin_category=row["admin_category"],
        meeting=meeting,
        symposium=symposium,
        time=time_obj,
    )

    # if record for this video already exists, alert user
    if not created:
        print("Video already exists in database; no new record created")
        return (
            "Video "
            + row["title"]
            + " already exists in database; no new record created\n"
        )
    # if record is new, add remaining details
    else:
        video.save()
        print("\nVideo saved")

        # add info for up to two speakers; any more will have to be added manually
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

        # get or create LCSH
        # add_lcsh_to_video(
        #     video,
        #     row["lcsh_topic"],
        #     row["lcsh_geographic"],
        #     row["lcsh_temporal"],
        #     row["lcsh_name_personal"],
        #     row["lcsh_name_corporate"],
        # )

        # add department and discipline
        departments = add_category_to_video(row["aps_departments"], APSDepartment)
        if departments:
            for department in departments:
                video.aps_departments.add(department)

        disciplines = add_category_to_video(
            row["academic_disciplines"], AcademicDiscipline
        )
        if disciplines:
            for discipline in disciplines:
                video.academic_disciplines.add(discipline)

        return reminders


# loop through spreadsheet, adding a video for each row
def add_videos():
    reminders = ""

    with open("videos.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                reminders += process_video(row)
            except Exception as e:
                print(f"An error occurred: {e}")
                reminders += "AN ERROR OCCURRED: " + row["title"] + "\n"

    if not reminders:
        reminders = "None"

    print("\n\n-----------\nReminders:\n" + reminders)
