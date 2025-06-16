import csv
import datetime
from zoneinfo import ZoneInfo
from meetingsvideos.models import Meeting, Video, LCSHTopic, LCSHGeographic, LCSHTemporal, LCSHNamePersonal, LCSHNameCorporate, AcademicDiscipline, APSDepartment, Symposium, Speaker, Affiliation

# converts EDTF date to datetime object
def process_time(str):
    lst = str.split("T")
    
    # process year, month, and day
    ymd = lst[0].split('-')

    year = int(ymd[0])
    month = int(ymd[1])
    day = int(ymd[2])

    # date_obj = date(year, month, day)
    
    # process time
    hms = lst[1].split(':')
    hour = int(hms[0])
    minute = int(hms[1])
    
    # time_obj = time(hour, minute)
    
    return datetime.datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("America/New_York"))

def process_diglib_url(str):
    lst = str.split(":")
    return lst[-1]

# takes as input string of LCSH headings (separated by semicolons if multiple); creates headings; returns list of Heading objects
def process_lcsh(lcsh, ModelName):
    if lcsh:
        lcsh_list = lcsh.split(';')
        headings = []
        for item in lcsh_list:
            # get or create LCSH
            obj, created = ModelName.objects.get_or_create(heading=item.strip())
            if created:
                print("New LCSH added: " + item.strip())
            headings.append(obj)
        return headings
    else:
        return []

# adds LCSH headings to video
def add_lcsh_to_video(video, topic, geographic, temporal, personal, corporate):
    lcsh_topic = process_lcsh(topic, LCSHTopic)
    for heading in lcsh_topic:
        video.lcsh_topic.add(heading)
        
    lcsh_geographic = process_lcsh(geographic, LCSHGeographic)
    for heading in lcsh_geographic:
        video.lcsh_geographic.add(heading)
        
    lcsh_temporal = process_lcsh(temporal, LCSHTemporal)
    for heading in lcsh_temporal:
        video.lcsh_temporal.add(heading)
        
    lcsh_name_personal = process_lcsh(personal, LCSHNamePersonal)
    for heading in lcsh_name_personal:
        video.lcsh_name_personal.add(heading)
        
    lcsh_name_corporate = process_lcsh(corporate, LCSHNameCorporate)
    for heading in lcsh_name_corporate:
        video.lcsh_name_corporate.add(heading)

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

def process_affiliation(affiliation_str, meeting, speaker):
    affiliation_str = affiliation_str.replace("|", "\n")
    affiliation, created = Affiliation.objects.get_or_create(meeting=meeting,
                                                             text=affiliation_str,
                                                             speaker=speaker)
    if created:
        affiliation.save()
        print("Affiliation created for speaker: " + speaker.display_name)
    return

# create speaker object and associated LCSH and affiliation
def process_speaker(lcsh, display_name, affiliation_str, meeting):
    # add LCSH for speaker, then create speaker
    # separate processes for personal name and corporate name
    if lcsh.startswith("corporate:"):
        lcsh = lcsh.replace("corporate:", "")
        speaker_lcsh = process_lcsh(lcsh, LCSHNameCorporate)[0]

        speaker, created = Speaker.objects.get_or_create(
            display_name=display_name,
            lcsh_name_corporate=speaker_lcsh)
    else:
        speaker_lcsh = process_lcsh(lcsh, LCSHNamePersonal)[0]

        speaker, created = Speaker.objects.get_or_create(
            display_name=display_name,
            lcsh_name_personal=speaker_lcsh)
    if created:
        speaker.save()
        print("Speaker added: " + speaker.display_name)
        
    # if affiliation, create new affiliation
    if affiliation_str:
        process_affiliation(affiliation_str, meeting, speaker)
    return speaker

# add speaker object to video
def add_speaker_to_video(video, lcsh, display_name, affiliation_str, meeting):
    if lcsh:
        speaker = process_speaker(lcsh, display_name, affiliation_str, meeting)
        video.speakers.add(speaker)

def process_symposium(str, meeting):
    reminders = ""
    if str:
        symposium, created = Symposium.objects.get_or_create(title=str,
                                                    meeting=meeting)
        if created:
            print("Symposium added: " + symposium.title)
            reminders += "**ADD MODERATOR INFO for the following symposium: " + str + "\n"
            
        return symposium, reminders
    else:
        return None, reminders

# process individual spreadsheet row to create video
def process_video(row):
    print("\n-----------\nVIDEO: " + row['title'] + "\n")
    
    # find correct meeting - search by name
    meeting = Meeting.objects.get(display_date=row['meeting'])
    
    # find or create symposium
    symposium, reminders = process_symposium(row['symposium'], meeting)
    
    # create date and time
    time_obj = process_time(row['time'])
    
    #TODO: let this update video object if not all data matches? which fields should ID it?
    video, created = Video.objects.get_or_create(title=row['title'],
                    lecture_additional_info=row['lecture_additional_info'],
                    abstract=row['abstract'],
                    opac=row['opac'],
                    service_file=row['service_file'],
                    youtube_url=row['youtube_url'],
                    display_notes=row['display_notes'],
                    admin_notes=row['admin_notes'],
                    diglib_node=process_diglib_url(row['diglib_url']),
                    admin_category = row['admin_category'],
                    meeting=meeting,
                    symposium=symposium,
                    time=time_obj
                    )
    
    # if record for this video already exists, alert user
    if not created:
        print("Video already exists in database; no new record created")
        return "Video " + row['title'] + " already exists in database; no new record created\n"
    # if record is new, add remaining details
    else:
        video.save()
        print("\nVideo saved")
        
        # add info for up to two speakers; any more will have to be added manually
        add_speaker_to_video(video, row['speaker_lcsh'], row['speaker_display_name'], row['speaker_affiliation'], meeting)
        
        add_speaker_to_video(video, row['speaker_2_lcsh'], row['speaker_2_display_name'], row['speaker_2_affiliation'], meeting)
        
        # get or create LCSH
        add_lcsh_to_video(video, row['lcsh_topic'], row['lcsh_geographic'], row['lcsh_temporal'], row['lcsh_name_personal'], row['lcsh_name_corporate'])
        
        departments = add_category_to_video(row['aps_departments'], APSDepartment)
        if departments:
            for department in departments:
                video.aps_departments.add(department)
        
        disciplines = add_category_to_video(row['academic_disciplines'], AcademicDiscipline)
        if disciplines:
            for discipline in disciplines:
                video.academic_disciplines.add(discipline)

        return reminders

# loop through spreadsheet, adding a video for each row
def add_videos():
    reminders = ""
    
    with open('videos.csv', newline='', encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                reminders += process_video(row)
            except Exception as e:
                print(f"An error occurred: {e}")
                reminders += "AN ERROR OCCURRED: " + row['title'] + "\n"
                       
    if not reminders:
        reminders = "None"
        
    print("\n\n-----------\nReminders:\n" + reminders)