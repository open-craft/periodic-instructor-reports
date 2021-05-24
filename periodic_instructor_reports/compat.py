"""
Proxies and edx-platform compatibility helper functions.
"""

# pylint: disable=import-error,import-outside-toplevel


def get_ccx_model() -> object:
    """
    Return CustomCourseForEdX (a.k.a CCX) model.
    """

    from lms.djangoapps.ccx.models import CustomCourseForEdX

    return CustomCourseForEdX
