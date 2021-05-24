"""
LMS user tasks application configuration Signal handlers are connected here.
"""

from django.apps import AppConfig


class PeriodicInstructorReportsConfig(AppConfig):
    """
    Application Configuration for preiodic_instructor_reports.
    """

    name = "periodic_instructor_reports"
    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "production": {
                    "relative_path": "settings",
                },
                "common": {
                    "relative_path": "settings",
                },
                "devstack": {
                    "relative_path": "settings",
                },
            },
        },
    }

    def ready(self):
        """
        Load signal handlers when the app is ready.
        """

        # pylint: disable=import-outside-toplevel
        from periodic_instructor_reports import signals

        assert signals
