# Generated by Django 5.1.2 on 2024-10-15 05:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_attendance"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("on_hold", "On Hold"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                (
                    "employees",
                    models.ManyToManyField(
                        blank=True, related_name="projects", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="managed_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
