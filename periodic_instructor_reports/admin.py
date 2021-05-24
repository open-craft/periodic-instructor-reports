"""
Django admin integration for periodic instructor reports.
"""

from django.contrib import admin
from periodic_instructor_reports.models import (
    PeriodicReportTask,
    PeriodicReportSchedule,
)


@admin.register(PeriodicReportTask)
class PeriodicReportTaskAdmin(admin.ModelAdmin):
    """
    Django admin widget for `PeriodicReportTask`s.
    """

    list_display = ["name", "path", "requires_request"]
    list_filter = ["name", "path", "requires_request"]
    search_fields = ["name", "path"]


@admin.register(PeriodicReportSchedule)
class PeriodicReportScheduleAdmin(admin.ModelAdmin):
    """
    Django admin widget for `PeriodicReportSchedule`s.
    """

    list_display = ["task", "interval", "courses", "arguments", "keyword_arguments"]
    list_filter = ["task__name", "course_ids"]
    search_fields = ["task__name", "task__path", "course_ids"]

    def courses(self, obj: PeriodicReportSchedule) -> str:
        """
        Return the formatted list of courses.
        """

        return ", ".join(list(obj.course_ids))
