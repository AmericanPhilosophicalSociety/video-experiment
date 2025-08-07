from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from .models import Video, Speaker, LCSH, AcademicDiscipline, APSDepartment
    

# takes a query and list of fields to search and returns a list of Q objects, chained with the "or" operator, performing both regular search and icontains search
def build_q_object(query, fields_to_search):
    search = Q()
    
    for field in fields_to_search:
        search_string = f'{field}__search'
        search_q = Q((search_string, query))
        search |= search_q
        
        icontains_string = f'{field}__icontains'
        icontains_q = Q((icontains_string, query))
        search |= icontains_q
    return search


# execute basic search
# searches title, abstract, speaker, and lcsh for search term
#TODO: fix this - using SearchVector gives a ton of duplicate results that aren't removed by duplicate(), issue seems to be searching on many-to-many field
def basic_search(query):
    query_lst = query.split()
    # query = SearchQuery(q)

    video_fields_to_search = ["title", "abstract", "speakers__display_name", "speakers__lcsh__heading", "lcsh__heading", "meeting__display_date", "academic_disciplines__name", "aps_departments__name"]
    speaker_fields_to_search = ["display_name", "lcsh__heading", "affiliation__position", "affiliation__institution"]
    subject_fields_to_search = ["heading"]
    discipline_fields_to_search = ["name"]
    department_fields_to_search = ["name"]
    #TODO: do we want to return symposium results? should this include ones where one video matches the search terms (so duplicating results from video search)?
    symposium_fields_to_search = ["title", "meeting__display_date"]
    
    video_search = Q()
    speaker_search = Q()
    subject_search = Q()
    discipline_search = Q()
    department_search = Q()
    
    for search_term in query_lst:
        video_search &= build_q_object(search_term, video_fields_to_search)
        speaker_search &= build_q_object(search_term, speaker_fields_to_search)
        subject_search &= build_q_object(search_term, subject_fields_to_search)
        discipline_search &= build_q_object(search_term, discipline_fields_to_search)
        department_search &= build_q_object(search_term, department_fields_to_search)
        
    videos = Video.objects.filter(video_search).distinct()
    # video_vector = SearchVector('title', 'abstract', 'lcsh__heading')
    # videos = Video.objects.annotate(search=video_vector).filter(search=query).distinct()
    
    speakers = Speaker.objects.filter(speaker_search).distinct()
    # speaker_vector = SearchVector('display_name', weight='A') + SearchVector('lcsh__heading', weight='B') + SearchVector('affiliation__position', 'affiliation__institution', weight='C')
    
    # search LCSH, excluding any associated only with speakers
    subjects = LCSH.objects.filter(subject_search).exclude(video=None)
    # subject_vector = SearchVector('heading')
    # subjects = LCSH.objects.annotate(search=subject_vector).filter(search=query).exclude(video=None)

    disciplines = AcademicDiscipline.objects.filter(discipline_search)
    departments = APSDepartment.objects.filter(department_search)
    
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
    
    title_fields_to_search = ["title"]
    title_search = build_q_object(title_q, title_fields_to_search)
    
    abstract_fields_to_search = ["abstract"]
    abstract_search = build_q_object(abstract_q, abstract_fields_to_search)
    
    speaker_fields_to_search = ["speakers__display_name", "speakers__lcsh__heading"]
    speaker_search = build_q_object(speaker_q, speaker_fields_to_search)

    subject_fields_to_search = ["lcsh__heading"]
    subject_search = build_q_object(subject_q, subject_fields_to_search)
    
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
    if categories:
        q_objects &= category_search
        
    return Video.objects.filter(q_objects).distinct()