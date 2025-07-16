from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from .models import Video, Speaker, LCSH
    
# execute basic search
# searches title, abstract, speaker, and lcsh for search term
#TODO: fix this - using SearchVector gives a ton of duplicate results that aren't removed by duplicate(), issue seems to be searching on many-to-many field
def basic_search(query):
    video_vector = SearchVector('title', 'abstract', 'lcsh__heading')

    # videos = Video.objects.annotate(search=video_vector).filter(search=query).distinct()
    videos = Video.objects.filter(Q(title__search=query) | Q(abstract__search=query) | Q(speakers__display_name__search=query) | Q(speakers__lcsh__heading__search=query) | Q(lcsh__heading__search=query)).distinct()
    
    # speaker_vector = SearchVector('display_name', weight='A') + SearchVector('lcsh__heading', weight='B') + SearchVector('affiliation__position', 'affiliation__institution', weight='C')
    speakers = Speaker.objects.filter(Q(display_name__search=query) | Q(lcsh__heading__search=query) | Q(affiliation__position__search=query) | Q(affiliation__institution__search=query)).distinct()
    
    # search LCSH, excluding any associated only with speakers
    subject_vector = SearchVector('heading')
    # subjects = LCSH.objects.filter(heading__search=query).exclude(video=None)
    subjects = LCSH.objects.annotate(search=subject_vector).filter(search=query).exclude(video=None)
    
    return videos, speakers, subjects