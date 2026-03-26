import csv, time, re
from loc_authorities.api import LocAPI, NameEntity, SubjectEntity, LocEntity
from wakepy import keep

"""
+ Takes a csv of videos as input
+ Outputs a csv of LCSH (validated where possible, plus suggestions that will need to be manually checked)
+ Matches are considered valid when the heading in the spreadsheet matches the aLabel or one of the vLabels for the record, OR (in the case of personal names) when a record appears in the names authority the beginning of which exactly matches what appears in the spreadsheet. This enables matches for names where Library of Congress includes birth or death dates, but our data doesn't.
"""

loc = LocAPI()


# query API for exact label
# returns ID for match
def query_api(heading):
    loc_id = None
    try:
        if heading.strip() != "":
            loc_id = loc.retrieve_label(heading)
            time.sleep(3)
            print(loc_id)
    except:
        print(f"label not found: {heading}")
    return loc_id


# replace comma separators with dash and query API
# returns ID for match
def dash_search(heading):
    if ", " in heading:
        heading_dashes = heading.replace(", ", "--")
        return query_api(heading_dashes)
    else:
        return None


# strip '__ century' and query API
# returns ID for match
def century_search(heading):
    century_regex = re.compile(r"(, |--)(\d)(\d)?(th|st|nd|rd)? century", re.I)
    match = century_regex.search(heading)
    if match:
        str_to_remove = match.group()
        heading_no_century = heading.replace(str_to_remove, "")
        result = query_api(heading_no_century)
        if result:
            return result
        result = dash_search(heading_no_century)
        if result:
            return result
    else:
        return None


# run keyword search
# returns ID for match
def keyword_search(heading, authority):
    search = loc.search(heading, authority)
    time.sleep(3)
    if search:
        return str(search[0].loc_id)
    else:
        return None


# run left-anchored search
# returns ID for match
def left_anchored_search(heading):
    suggest = loc.suggest(heading)
    time.sleep(3)
    if suggest:
        return str(suggest[0].loc_id)
    else:
        return None


# executes a series of alternate searches if no exact match found for heading
# returns (1) match ID and (2) boolean indicating whether this is a confirmed match
def handle_no_results(heading, is_personal_name):
    result = None

    # handle cases where personal name can't be found because birth/death dates are missing from our data
    if is_personal_name:
        result = left_anchored_search(heading)
        if result:
            if result.startswith("n"):
                entity = NameEntity(result)
                aLabel = str(entity.authoritative_label)
                if heading and aLabel.startswith(heading):
                    return result, True
                else:
                    return result, False
        # TODO: add logic to query viaf and orcid

    # if heading contains " ,", change to "--" and search again
    if not is_personal_name:
        result = dash_search(heading)
        if result:
            return result, True

    # if century specified, chop that off and search again
    # deprecating this for now since these should be valid LCSH, most just don't show up in the API
    # result = century_search(heading)
    # if result:
    #     return result, True

    # try left-anchored search
    result = left_anchored_search(heading)
    if result:
        return result, False

    # if no results, try keyword search
    result = keyword_search(heading, "subjects")
    if result:
        return result, False

    result = keyword_search(heading, "names")
    return result, False


# split spreadsheet cell on ; and return list of headings
def split_headings(string):
    if not string:
        return []
    else:
        lst = string.split(";")
        final_list = []
        for heading in lst:
            if heading.strip() != "":
                final_list.append(heading.strip())

        return final_list


# process list of headings and save info about matches to dictionary
def process_headings(
    headings, is_name, row, all_headings, category, is_speaker=False, display_name=None
):
    for heading in headings:
        is_match = False
        video_dict = {
            "talk_title": row["title"],
            "talk_date": row["date"],
            "order_in_day": row["order_in_day"],
            "is_speaker": is_speaker,
            "display_name": display_name,
        }

        # if heading hasn't already been searched, run search
        if heading not in all_headings:
            loc_id = query_api(heading)
            if loc_id:
                is_match = True
            if not loc_id:
                loc_id, is_match = handle_no_results(heading, is_name)

            # if valid LOC found, record some additional info to verify that this heading matches what's in the spreadsheet
            if loc_id:
                if loc_id.startswith("n"):
                    entity = NameEntity(loc_id)
                    aLabel = str(entity.authoritative_label)
                elif loc_id.startswith("sh"):
                    entity = SubjectEntity(loc_id)
                    aLabel = str(entity.authoritative_label)
                else:
                    try:
                        entity = LocEntity(loc_id)
                        aLabel = str(entity.authoritative_label)
                    except Exception as e:
                        aLabel = None
                        print(f"Error while processing heading {heading}: {e}")

                # add match to dictionary
                all_headings[heading] = {
                    "loc_id": loc_id,
                    "url": f"http://id.loc.gov/authorities/{loc_id}",
                    "aLabel": aLabel,
                    "headings_match": is_match,
                    "category": category,
                    "videos": [video_dict],
                }
            # if no valid LOC found, add to dictionary with loc_id value of None
            # include category from spreadsheet, which will be used to sort only local headings into approximate categories
            else:
                all_headings[heading] = {
                    "loc_id": loc_id,
                    "url": None,
                    "aLabel": None,
                    "headings_match": False,
                    "category": category,
                    "videos": [video_dict],
                }
        # if heading has been searched already, add another video to the dictionary for that heading
        else:
            all_headings[heading]["videos"].append(video_dict)


# process all spreadsheet cells that include LOC headings
def process_videos():
    all_headings = {}

    with open("videos.csv", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # TODO: this assumes that all speakers are personal names, but a few are organizations (e.g. Curtis Institute for Music). shouldn't be an issue if these match a valid LCSH, however
            if row["speaker_lcsh"]:
                process_headings(
                    [row["speaker_lcsh"]],
                    True,
                    row,
                    all_headings,
                    "PERSONAL_NAME",
                    is_speaker=True,
                    display_name=row["speaker_display_name"],
                )
            if row["speaker_2_lcsh"]:
                process_headings(
                    [row["speaker_2_lcsh"]],
                    True,
                    row,
                    all_headings,
                    "PERSONAL_NAME",
                    is_speaker=True,
                    display_name=row["speaker_2_display_name"],
                )

            topics = split_headings(row["lcsh_topic"])
            process_headings(topics, False, row, all_headings, "TOPIC")

            geographic = split_headings(row["lcsh_geographic"])
            process_headings(geographic, False, row, all_headings, "GEOGRAPHIC")

            temporal = split_headings(row["lcsh_temporal"])
            process_headings(temporal, False, row, all_headings, "OTHER")

            corporate = split_headings(row["lcsh_name_corporate"])
            process_headings(corporate, True, row, all_headings, "CORPORATE_NAME")

            personal_name = split_headings(row["lcsh_name_personal"])
            process_headings(personal_name, True, row, all_headings, "PERSONAL_NAME")

    return all_headings


# run script and write results to spreadsheet
def process_spreadsheet():
    loc_dict = process_videos()
    print(loc_dict)

    videos = []

    for key, value in loc_dict.items():
        for video in value["videos"]:
            video["orig_heading"] = key
            video["loc_id"] = value["loc_id"]
            video["category"] = value["category"]
            video["url"] = value["url"]
            video["aLabel"] = value["aLabel"]
            video["headings_match"] = value["headings_match"]
            videos.append(video)

    with open("lcsh.csv", "w", newline="", encoding="utf8") as csvfile:
        fieldnames = [
            "headings_match",
            "orig_heading",
            "aLabel",
            "loc_id",
            "category",
            "url",
            "talk_title",
            "talk_date",
            "order_in_day",
            "is_speaker",
            "display_name",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            try:
                writer.writerow(video)
            except:
                print(f"failed to write row for: {video['orig_heading']}")


def run_script():
    with keep.running():
        process_spreadsheet()
