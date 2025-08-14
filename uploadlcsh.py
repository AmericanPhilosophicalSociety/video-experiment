import csv
from meetingsvideos.models import LCSH, Video, Speaker
from uploadvideos import process_date


def process_category(rdftypes, lcshtype):
    if rdftypes:
        categories_list = rdftypes.split("|")
        category = categories_list[0]

        # TODO: clean this up
        if category == "Topic":
            return "TOPIC"
        elif category == "Title":
            return "TITLE"
        elif category == "Geographic":
            return "GEOGRAPHIC"
        elif category == "ComplexSubject":
            return "COMPLEX_SUBJECT"
        elif category == "PersonalName":
            return "PERSONAL_NAME"
        elif category == "CorporateName":
            return "CORPORATE_NAME"
        else:
            return "OTHER"
    else:
        if lcshtype == "lcsh_topic":
            return "TOPIC"
        elif lcshtype == "lcsh_geographic":
            return "GEOGRAPHIC"
        elif lcshtype == "lcsh_name_personal":
            return "PERSONAL_NAME"
        elif lcshtype == "lcsh_name_corporate":
            return "CORPORATE_NAME"
        else:
            return "OTHER"


def upload_lcsh():
    with open("lcsh.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                # determine appropriate heading and authority
                # different behavior based on whether this is a valid LCSH
                # TODO: how to accommodate alternate authorities like VIAF, ORCID?
                if row["aLabel"]:
                    heading = row["aLabel"]
                    authority = "LOC"
                else:
                    heading = row["orig_header"]
                    authority = "Local"

                # TODO: do this more efficiently, some kind of error checking
                category_controlled = process_category(
                    row["rdftypes"], row["lcsh_type"]
                )

                # trigger creation via API
                if row["token"]:
                    lcsh, created = LCSH.objects.get_or_create(
                        uri=row["token"], authority="LOC"
                    )

                else:
                    lcsh, created = LCSH.objects.get_or_create(
                        heading=heading,
                        uri=row["token"],
                        category=category_controlled,
                        authority=authority,
                    )

                    if created:
                        lcsh.save()
                        print("LCSH created: " + str(lcsh))

                # find video associated with lcsh
                date = process_date(row["talk_date"])
                video = Video.objects.get(title=row["talk_title"], date=date)

                # if lcsh is for a speaker, add to that speaker
                # speaker should already exist (created with affiliation during previous process)
                # TODO: can speaker be a corporate entity?
                if row["is_speaker"] == "TRUE":
                    speaker, created = Speaker.objects.get_or_create(
                        display_name=row["display_name"], video=video
                    )
                    speaker.lcsh = lcsh
                    speaker.save()
                    print("saved to speaker: " + str(speaker))
                # else, add to associated video
                else:
                    video.lcsh.add(lcsh)
                    video.save()
                    print("saved to video: " + str(video))
            except Exception as e:
                print(f"An error occurred: {e}")
