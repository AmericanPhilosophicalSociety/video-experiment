from django.db.models import Q
from .models import Video, Speaker, LCSH
    
# execute basic search
# searches title, abstract, speaker, and lcsh for search term
def basic_search(query):
    videos = Video.objects.filter(Q(title__icontains=query) | Q(abstract__icontains=query) | Q(speakers__display_name__icontains=query) | Q(speakers__lcsh__heading__icontains=query) | Q(lcsh__heading__icontains=query)).distinct()
    
    speakers = Speaker.objects.filter(Q(display_name__icontains=query) | Q(lcsh__heading__icontains=query) | Q(affiliation__position__icontains=query) | Q(affiliation__institution__icontains=query)).distinct()
    
    # search LCSH, excluding any associated only with speakers
    subjects = LCSH.objects.filter(heading__icontains=query).exclude(video=None)
    
    return videos, speakers, subjects