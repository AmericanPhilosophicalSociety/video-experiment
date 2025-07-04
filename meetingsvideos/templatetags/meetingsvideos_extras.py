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
