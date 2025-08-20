from django.db import models
from django.db.models.functions import Substr

from locpy.api import LocEntity, NameEntity, SubjectEntity


class AlphaManager(models.Manager):
    """Custom manager to include first letter of LCSH heading, for use
    in creating faceted lists"""
    def with_first_letter(self):
        return self.annotate(fl=Substr('lcsh__heading', 1, 1)).order_by("lcsh__heading")


class LCSHManager(models.Manager):
    """Only return LCSH headings when used as subjects"""
    def only_topics(self):
        return self.filter(video__isnull=False).distinct()


class LCSH(models.Model):
    heading = models.CharField(max_length=200)
    uri = models.CharField(max_length=200, blank=True, null=True)

    CATEGORY_CHOICES = {
        "PERSONAL_NAME": "Personal name",
        "CORPORATE_NAME": "Corporate name",
        "GEOGRAPHIC": "Geographic",
        "TOPIC": "Topic",
        "COMPLEX_SUBJECT": "Complex subject",
        "GENRE_FORM": "Genre/Form",
        "TITLE": "Title",
        "OTHER": "Other",
    }

    category = models.CharField(choices=CATEGORY_CHOICES, max_length=50)

    AUTHORITY_CHOICES = {
        "LOC": "LOC",
        "VIAF": "VIAF",
        "ORCID": "ORCID",
        "LOCAL": "Local",
        "OTHER": "Other",
    }

    authority = models.CharField(choices=AUTHORITY_CHOICES, max_length=50)

    components = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="component_of"
    )

    objects = LCSHManager()

    class Meta:
        verbose_name = "LCSH"
        verbose_name_plural = "LCSH"
        ordering = ["heading"]

    def __str__(self):
        return self.heading

    def without_dates(self):
        pass

    def save(self, **kwargs):
        # setting category as proxy for create vs update
        # make LOC subjects require lookup - change?
        if self.authority == "LOC" and not self.category:
            self.set_loc_data()
        super().save(**kwargs)
        # set components after save to avoid calling save method twice
        if self.category == "COMPLEX_SUBJECT" and not self.components.exists():
            self.get_components()

    @property
    def loc(self):
        uri = self.uri
        if uri.startswith("n"):
            entity = NameEntity(uri)
        elif uri.startswith("sh"):
            entity = SubjectEntity(uri)
        else:
            entity = LocEntity(uri)
        return entity

    def set_loc_data(self):
        category_mapping = {
            "http://www.loc.gov/mads/rdf/v1#PersonalName": "PERSONAL_NAME",
            "http://www.loc.gov/mads/rdf/v1#CorporateName": "CORPORATE_NAME",
            "http://www.loc.gov/mads/rdf/v1#Geographic": "GEOGRAPHIC",
            "http://www.loc.gov/mads/rdf/v1#Topic": "TOPIC",
            "http://www.loc.gov/mads/rdf/v1#ComplexSubject": "COMPLEX_SUBJECT",
            "http://www.loc.gov/mads/rdf/v1#Title": "TITLE",
            "http://www.loc.gov/mads/rdf/v1#GenreForm": "GENRE_FORM",
        }
        loc_entity = self.loc
        self.heading = str(loc_entity.authoritative_label)
        instances = [str(i) for i in loc_entity.instance_of]
        category = list(set(category_mapping.keys()).intersection(instances))[0]
        self.category = category_mapping[category]

    def get_components(self):
        loc_entity = self.loc
        for c in loc_entity.components:
            if isinstance(c, NameEntity) or isinstance(c, SubjectEntity):
                uri_stub = c.uri.split("/")[-1]
                component, _ = LCSH.objects.get_or_create(uri=uri_stub, authority="LOC")
                self.components.add(component)


class AcademicDiscipline(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class APSDepartment(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "APS department"


class Speaker(models.Model):
    display_name = models.CharField(
        max_length=200,
        help_text="The name as it would appear on a program, in order with no dates, e.g. 'Joyce Carol Oates'",
    )
    lcsh = models.ForeignKey(LCSH, blank=True, null=True, on_delete=models.SET_NULL)
    objects = AlphaManager()

    def __str__(self):
        return self.display_name

    def save(self, **kwargs):
        self.display_name = self.display_name.strip()
        super().save(**kwargs)

    def get_most_recent_affiliation(self):
        # TODO: change logic so this returns multiple affiliations if multiple affiliations are used in most recent video?
        if len(self.affiliation_set.all()) > 0:
            return self.affiliation_set.all().order_by("-meeting")[0]
        else:
            return ""

    class Meta:
        ordering = ["display_name"]


class Affiliation(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    meeting = models.ForeignKey("Meeting", on_delete=models.CASCADE)
    position = models.CharField(max_length=255, blank=True)
    institution = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.position and self.institution:
            affiliation_str = f"{self.position}\n{self.institution}"
        else:
            affiliation_str = f"{self.position}{self.institution}"
        return affiliation_str


class WithNotes(models.Model):
    """
    Includes display_notes field (for additional text to display on the page for a given Meeting, Video, etc.) and admin_notes field (for information attached to a record that should NOT be displayed publicly)
    """

    display_notes = models.TextField(
        blank=True, help_text="Additional text to display publicly"
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Use to attach additional information to record that will NOT display publicly",
    )

    class Meta:
        abstract = True


class Meeting(WithNotes):
    display_date = models.CharField(
        max_length=20,
        help_text="Human-readable date, e.g. 'November 2023' or 'April 2025",
    )
    start_date = models.DateField("First day of meeting - month, day, and year")
    end_date = models.DateField("Last day of meeting - month, day, and year")
    url = models.URLField(
        help_text="If this meeting has a page on the APS website, link it here",
        blank=True,
    )

    def videos_by_time(self):
        return self.video_set.all().order_by("date", "order_in_day")

    def __str__(self):
        return self.display_date

    class Meta:
        ordering = ["start_date"]


class ProgramInfo(WithNotes):
    title = models.CharField(max_length=200)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        self.title = self.title.strip()
        super().save(**kwargs)

    class Meta:
        abstract = True


class Symposium(ProgramInfo):
    moderators = models.ManyToManyField(Speaker, blank=True)

    def videos_by_time(self):
        return self.video_set.all().order_by("date", "order_in_day")

    class Meta:
        verbose_name_plural = "Symposia"
        ordering = ["title"]


class Video(ProgramInfo):
    lecture_additional_info = models.CharField(
        blank=True,
        help_text="e.g. '__ Memorial Lecture' or 'Keynote Lecture'",
        max_length=255,
    )
    symposium = models.ForeignKey(
        Symposium, blank=True, null=True, on_delete=models.SET_NULL
    )
    date = models.DateField("Month, day, and year.")
    order_in_day = models.IntegerField(default=0)
    speakers = models.ManyToManyField(Speaker, blank=True)
    abstract = models.TextField(blank=True)
    lcsh = models.ManyToManyField(LCSH, blank=True)
    # TODO: add validation for this
    doi = models.CharField(blank=True, max_length=255)
    diglib_pid = models.IntegerField(blank=True, null=True, unique=True)
    service_file = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    ADMIN_CATEGORY_CHOICES = {
        "ARCHIVES": "APS Archives",
        "INDUCTION": "Member Induction",
        "AWARDS": "Presentation of Awards",
        "CONCERT": "Concert",
        "LECTURE": "Lecture",
        "CONVERSATION": "In Conversation",
        "PANEL": "Panel Discussion",
        "OTHER": "Other",
    }

    admin_category = models.CharField(choices=ADMIN_CATEGORY_CHOICES, max_length=50)

    aps_departments = models.ManyToManyField(APSDepartment, blank=True)

    # add: default=Other
    academic_disciplines = models.ManyToManyField(AcademicDiscipline)

    def first_in_symposium(self):
        # videos = Symposium.objects.get(pk=self.symposium.pk)
        # videos = Video.objects.filter(symposium=self.symposium).order_by('time')
        if self.symposium:
            if self.symposium.videos_by_time()[0] == self:
                return True
        else:
            return False

    def get_prev(self):
        if self.symposium:
            videos = list(self.symposium.videos_by_time())
            i = videos.index(self)
            if i > 0:
                return videos[i - 1]
        else:
            return None

    def get_next(self):
        if self.symposium:
            videos = list(self.symposium.videos_by_time())
            i = videos.index(self)

            if i < len(videos) - 1:
                return videos[i + 1]
        else:
            return None

    class Meta:
        ordering = ["title"]
