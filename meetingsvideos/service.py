from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from .models import Video, Speaker, LCSH, AcademicDiscipline, APSDepartment
    

def build_q_object(query, search_type):
    pass

# execute basic search
# searches title, abstract, speaker, and lcsh for search term
#TODO: fix this - using SearchVector gives a ton of duplicate results that aren't removed by duplicate(), issue seems to be searching on many-to-many field
def basic_search(query):
    # query = SearchQuery(q)
    # video_vector = SearchVector('title', 'abstract', 'lcsh__heading')
    video_search = Q(title__search=query) | Q(abstract__search=query) | Q(speakers__display_name__search=query) | Q(speakers__lcsh__heading__search=query) | Q(lcsh__heading__search=query) | Q(meeting__display_date__search=query)
    
    video_icontains = Q(title__icontains=query) | Q(abstract__icontains=query) | Q(speakers__display_name__icontains=query) | Q(speakers__lcsh__heading__icontains=query) | Q(lcsh__heading__icontains=query) | Q(meeting__display_date__icontains=query)

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

def advanced_search(form):
    title_q = form.cleaned_data['title']
    abstract_q = form.cleaned_data['abstract']
    speaker_q = form.cleaned_data['speaker']
    subject_q = form.cleaned_data['subject']
    disciplines = form.cleaned_data['discipline']
    departments = form.cleaned_data['department']
    categories = form.cleaned_data['category']
    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']
    
    print(start_date)
    print(type(start_date))
    
    title_search = Q(title__search=title_q) | Q(title__icontains=title_q)
    abstract_search = Q(abstract__search=abstract_q) | Q(abstract__icontains=abstract_q)
    speaker_search = Q(speakers__display_name__search=speaker_q) | Q(speakers__display_name__icontains=speaker_q) | Q(speakers__lcsh__heading__search=speaker_q) | Q(speakers__lcsh__heading__icontains=speaker_q)
    subject_search = Q(lcsh__heading__search=subject_q) | Q(lcsh__heading__icontains=subject_q)
    
    discipline_search = Q(academic_disciplines__in=disciplines)
    department_search = Q(aps_departments__in=departments)
    
    category_search = Q(admin_category__in=categories)
    
    start_date_search = Q(date__gte=start_date)
    end_date_search = Q(date__lte=end_date)
    
    q_objects = Q()
    if title_q:
        q_objects &= title_search
    if abstract_q:
        q_objects &= abstract_search
    if speaker_q:
        q_objects &= speaker_search
    if subject_q:
        q_objects &= subject_search
    if disciplines:
        q_objects &= discipline_search
    if departments:
        q_objects &= department_search
    if start_date:
        q_objects &= start_date_search
    if end_date:
        q_objects &= end_date_search
        
    return Video.objects.filter(q_objects)