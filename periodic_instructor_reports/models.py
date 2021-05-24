"""
Django database models for periodic instructor reports scheduling.

This module contains all the models which are needed to easily schedule periodic
instructor reports from the Django admin UI.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from jsonfield.fields import JSONField


class PeriodicReportTask(models.Model):
    """
    Configuration model for all available report tasks which can be triggered.

    Since not all report tasks are prepared to be run as a periodic task, this
    model defines which tasks can be triggered. Also, this model does the
    bookeeping between task function names and their Python callable path.
    """

    name = models.CharField(
        max_length=254,
        help_text="Name of the task. Used for representation purposes on the Admin UI.",
    )
    path = models.CharField(
        max_length=254,
        help_text="""Python path of the task need to be called periodically. Example:
        lms.djangoapps.instructor_task.api.submit_calculate_students_features_csv""",
    )
    requires_request = models.BooleanField(
        default=False,
        help_text="Indicates if the task requires a requests as a first parameter.",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.path})"

    # pylint: disable=missing-class-docstring,too-few-public-methods
    class Meta:
        verbose_name = _("Periodic report task")
        verbose_name_plural = _("Periodic report tasks")
        unique_together = ["name", "path"]


class PeriodicReportSchedule(models.Model):
    """
    TODO: Add description
    """

    STRUCTURE_REGULAR = "regular"
    STRUCTURE_BY_DATE = "by_date"

    UPLOAD_FOLDER_STRUCTURES = (
        (STRUCTURE_REGULAR, STRUCTURE_REGULAR),
        (STRUCTURE_BY_DATE, STRUCTURE_BY_DATE),
    )

    task = models.ForeignKey("PeriodicReportTask", on_delete=models.CASCADE)
    owner = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        help_text="The user who created the periodic report task.",
    )
    celery_task = models.ForeignKey(
        PeriodicTask,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.CASCADE,
    )
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE)
    course_ids = JSONField(
        default=list(),
        help_text="List of course and CCX course IDs to run the reports against.",
        null=False,
        blank=False,
    )
    arguments = JSONField(
        default=list(),
        null=True,
        blank=True,
        help_text="List of arguments passed to the task.",
    )
    keyword_arguments = JSONField(
        default=dict(),
        null=True,
        blank=True,
        help_text="Keyword arguments passed to the task.",
    )
    include_ccx = models.BooleanField(
        default=False,
        help_text="""If set to True, the listed courses' related ccx courses will be included in
        the report generation.
        """,
    )
    only_ccx = models.BooleanField(
        default=False, help_text="Run the task execution only against CCX courses."
    )
    upload_folder_prefix = models.CharField(
        max_length=254,
        default="",
        help_text="""Prefix of the upload folder. In case a prefix ends with a trailing slash,
        a new folder will be created.
        """
    )
    upload_folder_structure = models.CharField(
        choices=UPLOAD_FOLDER_STRUCTURES,
        max_length=32,
        default=STRUCTURE_REGULAR,
        help_text="Define the folder structure during upload.",
    )

    def __str__(self) -> str:
        return f"{self.task} ({self.interval})"

    # pylint: disable=missing-class-docstring,too-few-public-methods
    class Meta:
        verbose_name = _("Periodic report schedule")
        verbose_name_plural = _("Periodic report schedules")
