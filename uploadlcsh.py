import csv
from meetingsvideos.models import (
    LCSH,
    Video,
)
from uploadvideos import process_time


def process_category(rdftypes, lcshtype):
    if rdftypes:
        categories_list = rdftypes.split("|")
        category = categories_list[0]
        
        if category == "Topic" or category == "Title" or category == "Geographic":
            return category
        elif category == "ComplexSubject":
            return "Complex subject"
        elif category == "PersonalName":
            return "Personal name"
        elif category == "CorporateName":
            return "Corporate name"
        else:
            return "Other"   
    else:
        if lcshtype == "lcsh_topic":
            return "Topic"
        elif lcshtype == "lcsh_geographic":
            return "Geographic"
        elif lcshtype == "lcsh_name_personal":
            return "Personal name"
        elif lcshtype == "lcsh_name_corporate":
            return "Corporate name"
        else:
            return "Other"
        
def upload_lcsh():
    with open("lcsh.csv", newline="", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                # determine appropriate heading and authority
                # different behavior based on whether this is a valid LCSH
                #TODO: how to accommodate alternate authorities like VIAF, ORCID?
                if row["aLabel"]:
                    heading = row["aLabel"]
                    authority = "LOC"
                else:
                    heading = row["orig_header"]
                    authority = "Local"
                    
                #TODO: do this more efficiently, some kind of error checking
                category_controlled = process_category(row["rdftypes"], row["lcsh_type"])
                
                lcsh, created = LCSH.objects.get_or_create(
                    heading=heading,
                    uri=row["token"],
                    category=category_controlled,
                    authority=authority,
                )
                
                if created:
                    lcsh.save()
                    print("LCSH created: " + str(lcsh))
                
                # find video and add LCSH to it
                time = process_time(row["talk_time"])
                video = Video.objects.get(title=row["talk_title"], time=time)
                video.lcsh.add(lcsh)
                video.save()
                print("saved to video: " + str(video))
            except Exception as e:
                print(f"An error occurred: {e}")