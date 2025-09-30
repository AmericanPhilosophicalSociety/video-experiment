from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_affiliation(context):
    speaker = context["speaker"]
    video = context["video"]
    meeting = video.meeting
    affiliation = speaker.get_affiliation(meeting.pk)
    if affiliation:
        return affiliation.text.replace("\n", "<br>")
    else:
        return None
    # return speaker.get_affiliation(meeting.pk)


@register.filter
def pagination_offset(value):
    if int(value) == 1:
        return 0
    else:
        return int(value) * 10


@register.filter
def filter_affiliations(value, meeting):
    return value.filter(meetings=meeting)
