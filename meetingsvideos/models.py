from django.db import models
from django.urls import reverse

class LCSH(models.Model):
    heading = models.CharField(max_length = 200)
    # token = models.CharField(max_length = 200, unique=True)
    
    #TODO: rdftypes?
    
    def __str__(self):
        return self.heading
    
    def save(self, **kwargs):
        while self.heading[-1] == " " or self.heading[-1] == ",":
            self.heading = self.heading.strip().rstrip(",")
        super().save(**kwargs)
    
    class Meta:
        abstract = True
        
class LCSHTopic(LCSH):
    def get_absolute_url(self):
        return reverse("topic_detail", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "Topic (LCSH)"
        verbose_name_plural = "Topics (LCSH)"
        ordering = ['heading']

class LCSHGeographic(LCSH):
    def get_absolute_url(self):
        return reverse("geographic_detail", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "Geographic (LCSH)"
        verbose_name_plural = "Geographic (LCSH)"
        ordering = ['heading']

class LCSHTemporal(LCSH):
    def get_absolute_url(self):
        return reverse("temporal_detail", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "Temporal (LCSH)"
        verbose_name_plural = "Temporal (LCSH)"
        ordering = ['heading']

class LCSHNamePersonal(LCSH):
    def get_absolute_url(self):
        return reverse("name_detail", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "Personal name (LCSH)"
        verbose_name_plural = "Personal names (LCSH)"
        ordering = ['heading']

class LCSHNameCorporate(LCSH):
    def get_absolute_url(self):
        return reverse("corporate_detail", kwargs={"pk": self.pk})
    
    class Meta:
        verbose_name = "Corporate name (LCSH)"
        verbose_name_plural = "Corporate names (LCSH)"
        ordering = ['heading']

class CategoryChoice(models.Model):
    name = models.CharField(max_length = 50)
    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True
    
class AcademicDiscipline(CategoryChoice):
    pass

class APSDepartment(CategoryChoice):
    class Meta:
        verbose_name = "APS department"

class Speaker(models.Model):
    display_name = models.CharField(max_length = 200, 
                                    help_text = "The name as it would appear on a program, in order with no dates, e.g. 'Joyce Carol Oates'")
    lcsh_name_personal = models.ForeignKey(LCSHNamePersonal, 
                                     blank=True, 
                                     null=True, 
                                     on_delete = models.SET_NULL)
    lcsh_name_corporate = models.ForeignKey(LCSHNameCorporate, 
                                      blank=True, 
                                      null=True, 
                                      on_delete = models.SET_NULL,
                                      help_text = "Use only if the 'Speaker' of the talk is an organization and not an individual, e.g. if an orchestra gives a concert")
    
    def get_affiliation(self, meeting_pk):
        affiliation = self.affiliation_set.filter(meeting__pk=meeting_pk)
        if affiliation:
            return affiliation[0]
        else:
            return None
    
    def __str__(self):
        return self.display_name
    
    def save(self, **kwargs):
        self.display_name = self.display_name.strip()
        super().save(**kwargs)
    
    class Meta:
        ordering = ['display_name']
    
class Affiliation(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    text = models.TextField(max_length = 1000)
    
    def __str__(self):
        return self.text

class WithNotes(models.Model):
    """
    Includes display_notes field (for additional text to display on the page for a given Meeting, Video, etc.) and admin_notes field (for information attached to a record that should NOT be displayed publicly)
    """
    display_notes = models.TextField(max_length = 1000, blank=True, help_text="Additional text to display publicly")
    admin_notes = models.TextField(max_length = 1000, blank=True, help_text="Use to attach additional information to record that will NOT display publicly")
    
    class Meta:
        abstract = True

class Meeting(WithNotes):
    display_date = models.CharField(max_length = 20, help_text = "Human-readable date, e.g. 'November 2023' or 'April 2025")
    start_date = models.DateField("First day of meeting - month, day, and year")
    end_date = models.DateField("Last day of meeting - month, day, and year")
    url = models.URLField(help_text="If this meeting has a page on the APS website, link it here", blank=True)
    
    def videos_by_time(self):
        return self.video_set.all().order_by('time')
    
    def __str__(self):
        return self.display_date
    
    class Meta:
        ordering = ['start_date']

class ProgramInfo(WithNotes):
    title = models.CharField(max_length = 200)
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
        return self.video_set.all().order_by('time')
    
    class Meta:
        verbose_name_plural = "Symposia"
        ordering = ['title']
    
class Video(ProgramInfo):
    lecture_additional_info = models.CharField(blank=True, help_text="e.g. '__ Memorial Lecture' or 'Keynote Lecture'", max_length = 255)
    symposium = models.ForeignKey(Symposium,
                                  blank=True,
                                  null=True,
                                  on_delete = models.SET_NULL)
    time = models.DateTimeField("Month, day, year, and time. If time is unknown, make up times that will preserve the correct order of the videos.")
    speakers = models.ManyToManyField(Speaker, blank=True)
    abstract = models.TextField(max_length = 1000, blank=True)
    lcsh_topic = models.ManyToManyField(LCSHTopic, blank=True)
    lcsh_geographic = models.ManyToManyField(LCSHGeographic, blank=True)
    lcsh_temporal = models.ManyToManyField(LCSHTemporal, blank=True)
    lcsh_name_personal = models.ManyToManyField(LCSHNamePersonal, blank=True)
    lcsh_name_corporate = models.ManyToManyField(LCSHNameCorporate, blank=True)
    opac = models.URLField(blank=True, null=True)
    # add validation for this
    doi = models.CharField(blank=True, max_length = 255)
    diglib_node = models.IntegerField(blank=True, null=True, unique=True)
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
        "OTHER": "Other"
    }
    
    admin_category = models.CharField(
        choices=ADMIN_CATEGORY_CHOICES,
        max_length = 50
    )
    
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
                return videos[i-1]
        else:
            return None
        
    def get_next(self):
        if self.symposium:
            videos = list(self.symposium.videos_by_time())
            i = videos.index(self)
            
            if i < len(videos) - 1:
                return videos[i+1]
        else:
            return None
    
    class Meta:
        ordering = ['title']