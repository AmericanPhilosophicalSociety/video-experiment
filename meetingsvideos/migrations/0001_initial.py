# Generated by Django 5.1 on 2025-06-16 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AcademicDiscipline",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="APSDepartment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "APS department",
            },
        ),
        migrations.CreateModel(
            name="LCSHGeographic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("heading", models.CharField(max_length=200, unique=True)),
            ],
            options={
                "verbose_name": "Geographic (LCSH)",
                "verbose_name_plural": "Geographic (LCSH)",
                "ordering": ["heading"],
            },
        ),
        migrations.CreateModel(
            name="LCSHNameCorporate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("heading", models.CharField(max_length=200, unique=True)),
            ],
            options={
                "verbose_name": "Corporate name (LCSH)",
                "verbose_name_plural": "Corporate names (LCSH)",
                "ordering": ["heading"],
            },
        ),
        migrations.CreateModel(
            name="LCSHNamePersonal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("heading", models.CharField(max_length=200, unique=True)),
            ],
            options={
                "verbose_name": "Personal name (LCSH)",
                "verbose_name_plural": "Personal names (LCSH)",
                "ordering": ["heading"],
            },
        ),
        migrations.CreateModel(
            name="LCSHTemporal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("heading", models.CharField(max_length=200, unique=True)),
            ],
            options={
                "verbose_name": "Temporal (LCSH)",
                "verbose_name_plural": "Temporal (LCSH)",
                "ordering": ["heading"],
            },
        ),
        migrations.CreateModel(
            name="LCSHTopic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("heading", models.CharField(max_length=200, unique=True)),
            ],
            options={
                "verbose_name": "Topic (LCSH)",
                "verbose_name_plural": "Topics (LCSH)",
                "ordering": ["heading"],
            },
        ),
        migrations.CreateModel(
            name="Meeting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "display_notes",
                    models.TextField(
                        blank=True,
                        help_text="Additional text to display publicly",
                        max_length=1000,
                    ),
                ),
                (
                    "admin_notes",
                    models.TextField(
                        blank=True,
                        help_text="Use to attach additional information to record that will NOT display publicly",
                        max_length=1000,
                    ),
                ),
                (
                    "display_date",
                    models.CharField(
                        help_text="Human-readable date, e.g. 'November 2023' or 'April 2025",
                        max_length=20,
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        verbose_name="First day of meeting - month, day, and year"
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        verbose_name="Last day of meeting - month, day, and year"
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        blank=True,
                        help_text="If this meeting has a page on the APS website, link it here",
                    ),
                ),
            ],
            options={
                "ordering": ["start_date"],
            },
        ),
        migrations.CreateModel(
            name="Speaker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "display_name",
                    models.CharField(
                        help_text="The name as it would appear on a program, in order with no dates, e.g. 'Joyce Carol Oates'",
                        max_length=200,
                    ),
                ),
                (
                    "lcsh_name_corporate",
                    models.ForeignKey(
                        blank=True,
                        help_text="Use only if the 'Speaker' of the talk is an organization and not an individual, e.g. if an orchestra gives a concert",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="meetingsvideos.lcshnamecorporate",
                    ),
                ),
                (
                    "lcsh_name_personal",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="meetingsvideos.lcshnamepersonal",
                    ),
                ),
            ],
            options={
                "ordering": ["display_name"],
            },
        ),
        migrations.CreateModel(
            name="Affiliation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(max_length=1000)),
                (
                    "meeting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingsvideos.meeting",
                    ),
                ),
                (
                    "speaker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingsvideos.speaker",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Symposium",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "display_notes",
                    models.TextField(
                        blank=True,
                        help_text="Additional text to display publicly",
                        max_length=1000,
                    ),
                ),
                (
                    "admin_notes",
                    models.TextField(
                        blank=True,
                        help_text="Use to attach additional information to record that will NOT display publicly",
                        max_length=1000,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "meeting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingsvideos.meeting",
                    ),
                ),
                (
                    "moderators",
                    models.ManyToManyField(blank=True, to="meetingsvideos.speaker"),
                ),
            ],
            options={
                "verbose_name_plural": "Symposia",
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "display_notes",
                    models.TextField(
                        blank=True,
                        help_text="Additional text to display publicly",
                        max_length=1000,
                    ),
                ),
                (
                    "admin_notes",
                    models.TextField(
                        blank=True,
                        help_text="Use to attach additional information to record that will NOT display publicly",
                        max_length=1000,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "lecture_additional_info",
                    models.CharField(
                        blank=True,
                        help_text="e.g. '__ Memorial Lecture' or 'Keynote Lecture'",
                        max_length=255,
                    ),
                ),
                (
                    "time",
                    models.DateTimeField(
                        verbose_name="Month, day, year, and time. If time is unknown, make up times that will preserve the correct order of the videos."
                    ),
                ),
                ("abstract", models.TextField(blank=True, max_length=1000)),
                ("opac", models.URLField(blank=True, null=True)),
                ("doi", models.CharField(blank=True, max_length=255)),
                (
                    "diglib_node",
                    models.IntegerField(blank=True, null=True, unique=True),
                ),
                ("service_file", models.URLField(blank=True, null=True)),
                ("youtube_url", models.URLField(blank=True, null=True)),
                (
                    "admin_category",
                    models.CharField(
                        choices=[
                            ("ARCHIVES", "APS Archives"),
                            ("INDUCTION", "Member Induction"),
                            ("AWARDS", "Presentation of Awards"),
                            ("CONCERT", "Concert"),
                            ("LECTURE", "Lecture"),
                            ("CONVERSATION", "In Conversation"),
                            ("PANEL", "Panel Discussion"),
                            ("OTHER", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "academic_disciplines",
                    models.ManyToManyField(to="meetingsvideos.academicdiscipline"),
                ),
                (
                    "aps_departments",
                    models.ManyToManyField(
                        blank=True, to="meetingsvideos.apsdepartment"
                    ),
                ),
                (
                    "lcsh_geographic",
                    models.ManyToManyField(
                        blank=True, to="meetingsvideos.lcshgeographic"
                    ),
                ),
                (
                    "lcsh_name_corporate",
                    models.ManyToManyField(
                        blank=True, to="meetingsvideos.lcshnamecorporate"
                    ),
                ),
                (
                    "lcsh_name_personal",
                    models.ManyToManyField(
                        blank=True, to="meetingsvideos.lcshnamepersonal"
                    ),
                ),
                (
                    "lcsh_temporal",
                    models.ManyToManyField(
                        blank=True, to="meetingsvideos.lcshtemporal"
                    ),
                ),
                (
                    "lcsh_topic",
                    models.ManyToManyField(blank=True, to="meetingsvideos.lcshtopic"),
                ),
                (
                    "meeting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingsvideos.meeting",
                    ),
                ),
                (
                    "speakers",
                    models.ManyToManyField(blank=True, to="meetingsvideos.speaker"),
                ),
                (
                    "symposium",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="meetingsvideos.symposium",
                    ),
                ),
            ],
            options={
                "ordering": ["title"],
            },
        ),
    ]
