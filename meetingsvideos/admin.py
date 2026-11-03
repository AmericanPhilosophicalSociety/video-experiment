from django.contrib import admin
from .models import (
    LCSH,
    AcademicDiscipline,
    APSDepartment,
    Speaker,
    Affiliation,
    Meeting,
    Symposium,
    Video,
)


# Register your models here.
class LCSHAdmin(admin.ModelAdmin):
    pass


admin.site.register(LCSH, LCSHAdmin)


class AcademicDisciplineAdmin(admin.ModelAdmin):
    pass


admin.site.register(AcademicDiscipline, AcademicDisciplineAdmin)


class APSDepartmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(APSDepartment, APSDepartmentAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Speaker, SpeakerAdmin)


class AffiliationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Affiliation, AffiliationAdmin)


class MeetingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Meeting, MeetingAdmin)


class SymposiumAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "meeting",
    )


admin.site.register(Symposium, SymposiumAdmin)


class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "meeting",
    )


admin.site.register(Video, VideoAdmin)
