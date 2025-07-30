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
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.
class LCSHAdmin(admin.ModelAdmin):
    pass


# class LCSHTopicResource(resources.ModelResource):
#     class Meta:
#         model = LCSHTopic

admin.site.register(LCSH, LCSHAdmin)


class AcademicDisciplineAdmin(admin.ModelAdmin):
    pass


class AcademicDisciplineResource(resources.ModelResource):
    class Meta:
        model = AcademicDiscipline


class AcademicDisciplineAdmin(ImportExportModelAdmin):
    resource_classes = [AcademicDisciplineResource]


admin.site.register(AcademicDiscipline, AcademicDisciplineAdmin)


class APSDepartmentAdmin(admin.ModelAdmin):
    pass


class APSDepartmentResource(resources.ModelResource):
    class Meta:
        model = APSDepartment


class APSDepartmentAdmin(ImportExportModelAdmin):
    resource_classes = [APSDepartmentResource]


admin.site.register(APSDepartment, APSDepartmentAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Speaker, SpeakerAdmin)


class AffiliationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Affiliation, AffiliationAdmin)


class MeetingAdmin(admin.ModelAdmin):
    pass


class MeetingResource(resources.ModelResource):
    class Meta:
        model = Meeting


class MeetingAdmin(ImportExportModelAdmin):
    resource_classes = [MeetingResource]


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
