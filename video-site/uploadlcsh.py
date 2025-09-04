import csv
from meetingsvideos.models import LCSH, Video, Speaker
from uploadvideos import process_date


def upload_lcsh():
    with open("lcsh.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if row["headings_match"] == "True":
                try:
                    heading = row["aLabel"]
                    authority = "LOC"
                    
                    lcsh, created = LCSH.objects.get_or_create(
                        heading=heading,
                        uri=row["loc_id"],
                        authority=authority,
                    )

                    if created:
                        lcsh.save()
                        # print("LCSH created: " + str(lcsh))

                    # find video associated with lcsh
                    date = process_date(row["talk_date"])
                    video = Video.objects.get(title=row["talk_title"], date=date, order_in_day=row["order_in_day"])

                    # if lcsh is for a speaker, add to that speaker
                    # speaker should already exist (created with affiliation during previous process)
                    if row["is_speaker"] == "True":
                        speaker, created = Speaker.objects.get_or_create(
                            display_name=row["display_name"], video=video
                        )
                        speaker.lcsh = lcsh
                        speaker.save()
                        # print("saved to speaker: " + str(speaker))
                    # else, add to associated video
                    else:
                        video.lcsh.add(lcsh)
                        video.save()
                        # print("saved to video: " + str(video))
                except Exception as e:
                    print(f"An error occurred while processing header {row["aLabel"]} ({row['loc_id']}): {e}")
