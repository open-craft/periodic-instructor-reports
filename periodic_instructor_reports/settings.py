"""
Django Plugin App settings.
"""

import os


def get_setting(settings, setting_key, default_val=""):
    """
    Retrieves the value of the requested setting

    Gets the Value of an Environment variable either from
    the OS Environment or from the settings ENV_TOKENS

    Arguments:
        - settings (dict): Django settings
        - setting_key (str): String
        - default_val (str): Optional String

    Returns:
        - Value of the requested setting (String)
    """

    setting_val = os.environ.get(setting_key, default_val)

    if hasattr(settings, "ENV_TOKENS"):
        return settings.ENV_TOKENS.get(setting_key, setting_val)

    return setting_val


def plugin_settings(settings):
    """
    Specifies django environment settings
    """

    # Set the celery beat scheduler to database scheduler if not defined.
    # In case the scheduler is set to something else than `DatabaseScheduler`,
    # the plugin app may not work as expected or not schedule tasks at all.
    settings.CELERYBEAT_SCHEDULER = get_setting(
        settings,
        "CELERYBEAT_SCHEDULER",
        default_val="django_celery_beat.schedulers:DatabaseScheduler",
    )
