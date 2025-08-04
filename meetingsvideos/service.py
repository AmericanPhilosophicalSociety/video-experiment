from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from .models import Video, Speaker, LCSH, AcademicDiscipline, APSDepartment
    
# execute basic search
# searches title, abstract, speaker, and lcsh for search term
#TODO: fix this - using SearchVector gives a ton of duplicate results that aren't removed by duplicate(), issue seems to be searching on many-to-many field
def basic_search(query):
    # query = SearchQuery(q)
    # video_vector = SearchVector('title', 'abstract', 'lcsh__heading')
    video_search = Q(title__search=query) | Q(title__search=query) | Q(abstract__search=query) | Q(speakers__display_name__search=query) | Q(speakers__lcsh__heading__search=query) | Q(lcsh__heading__search=query)
    
    video_icontains = Q(title__icontains=query) | Q(title__icontains=query) | Q(abstract__icontains=query) | Q(speakers__display_name__icontains=query) | Q(speakers__lcsh__heading__icontains=query) | Q(lcsh__heading__icontains=query)

    # videos = Video.objects.annotate(search=video_vector).filter(search=query).distinct()
    videos = Video.objects.filter(video_search | video_icontains).distinct()
    
    # speaker_vector = SearchVector('display_name', weight='A') + SearchVector('lcsh__heading', weight='B') + SearchVector('affiliation__position', 'affiliation__institution', weight='C')
    speaker_search = Q(display_name__search=query) | Q(lcsh__heading__search=query) | Q(affiliation__position__search=query) | Q(affiliation__institution__search=query)
    
    speaker_icontains = Q(display_name__icontains=query) | Q(lcsh__heading__icontains=query) | Q(affiliation__position__icontains=query) | Q(affiliation__institution__icontains=query)
    
    speakers = Speaker.objects.filter(speaker_search | speaker_icontains).distinct()
    
    # search LCSH, excluding any associated only with speakers
    # subject_vector = SearchVector('heading')
    # subjects = LCSH.objects.annotate(search=subject_vector).filter(search=query).exclude(video=None)
    subjects = LCSH.objects.filter(Q(heading__search=query) | Q(heading__icontains=query)).exclude(video=None)
    
    disciplines = AcademicDiscipline.objects.filter(Q(name__search=query) | Q(name__icontains=query))
    
    departments = APSDepartment.objects.filter(Q(name__search=query) | Q(name__icontains=query))
    
    return videos, speakers, subjects, disciplines, departments