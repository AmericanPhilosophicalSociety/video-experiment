from django.db.models import Q
from .models import Video
    
# BEGIN HELPER FUNCTIONS - SEARCH (GENERAL)

# returns list of Q objects that search for a single query term in the appropriate fields in Sentence or Text
# Q object is True if query term is found in any one of the two fields
def build_q_object(q, search_type):
    q_objects = Q()

    if search_type == "sentence":
        q_objects |= Q(gls_en__icontains=q)
    elif search_type == "text":
        q_objects |= Q(sentence__gls_en__icontains=q)

    q_objects |= Q(word__txt_tun__icontains=q)
    # q_objects |= Q(morpheme__txt_tun__icontains=q)

    return q_objects

# execute basic search
def basic_search(query):
    sentence_q_objects = build_q_object(query, "sentence")
    sentences = Sentence.objects.filter(sentence_q_objects).distinct()

    # this is used in template to access appropriate dictionary entries
    senses = Sense.objects.filter(
        Q(gloss_en__icontains=query) | Q(entry__lexical_unit_tun__icontains=query)
        ).distinct('entry')
    
    morphemes = Morpheme.objects.filter(
        Q(txt_tun__icontains=query) | Q(gls_en__icontains=query)
    ).distinct("type", "txt_tun")
    
    return [sentences, senses, morphemes]