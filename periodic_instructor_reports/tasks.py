"""
Celery tasks used to handle periodic instructor reporting.

By default, edX platform cannot run instructor reports in a periodic way, hence
we need a wrapper around them. This module contains the wrapper logic to
schedule instructor (or other, capable) tasks in a periodic manner. A task is
capable to run initiated by the wrapper if it can accept `*args` and `**kwargs`.

Since instructor tasks requires an HTTP request to passed to the task or its
wrapper, we need to fake an HTTP request manually. To determine the user for
`request.user` we use the user who created the periodic report schedule.
"""

import hashlib
from datetime import date
from importlib import import_module
from typing import Tuple, Callable

from celery import shared_task
from celery.utils.log import get_task_logger

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from periodic_instructor_reports.compat import get_ccx_model
from periodic_instructor_reports.models import PeriodicReportSchedule


logger = get_task_logger(__name__)


def get_function_from_path(path: str) -> Callable:
    """
    Import a Python function dynamically and return it as a callable.
    """

    *module_parts, function = path.split(".")
    module = ".".join(module_parts)

    globals()[module] = import_module(module)
    return getattr(globals()[module], function)


def create_fake_request(user: User) -> HttpRequest:
    """
    Create a fake `HttpRequest` to satisfy instructor task wrapper functions.
    """

    request = HttpRequest()
    request.user = user
    request.META = {
        "REMOTE_ADDR": "0.0.0.0",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": 0,
    }

    return request


@shared_task
def periodic_task_wrapper(periodic_task_schedule_id: int) -> None:
    """
    Wrapper for executing instructor or other capable tasks in a periodic way.

    The target task's path is dynamically imported and executed with the pre-defined arguments and
    keyword arguments.
    """

    logger.debug(f"Received task for schedule {periodic_task_schedule_id}")

    # pylint: disable=no-member
    schedule: PeriodicReportSchedule = PeriodicReportSchedule.objects.get(
        id=periodic_task_schedule_id
    )

    report_task = get_function_from_path(schedule.task.path)

    target_course_ids = [
        SlashSeparatedCourseKey.from_string(course_id)
        for course_id in schedule.course_ids
    ]

    if schedule.include_ccx:
        ccx_model = get_ccx_model()
        custom_courses = ccx_model.objects.filter(course_id__in=schedule.course_ids)
        ccx_course_ids = list({ccx.locator for ccx in custom_courses})

        if schedule.only_ccx:
            target_course_ids = ccx_course_ids
        else:
            target_course_ids.extend(ccx_course_ids)

    logger.info(f"Calling {report_task} for {target_course_ids}")

    for course_id in target_course_ids:
        task_call_args = [course_id, *schedule.arguments]
        task_call_kwargs = {**schedule.keyword_arguments}

        if schedule.task.requires_request:
            task_call_args.insert(0, create_fake_request(schedule.owner))

        if schedule.upload_folder_structure == PeriodicReportSchedule.STRUCTURE_FLAT:
            task_call_kwargs.update({
                "upload_parent_dir": schedule.upload_folder_prefix,
            })
        elif schedule.upload_folder_structure == PeriodicReportSchedule.STRUCTURE_REGULAR:
            hashed_course_id = hashlib.sha1(str(course_id).encode('utf-8')).hexdigest()
            task_call_kwargs.update({
                "upload_parent_dir": "{directory_prefix}{directory_name}".format(
                    directory_prefix=schedule.upload_folder_prefix,
                    directory_name=hashed_course_id,
                )
            })
        elif schedule.upload_folder_structure == PeriodicReportSchedule.STRUCTURE_BY_DATE:
            task_call_kwargs.update({
                "upload_parent_dir": "{directory_prefix}{directory_name}".format(
                    directory_prefix=schedule.upload_folder_prefix,
                    directory_name=date.today().strftime("%Y/%m/%d"),
                )
            })

        report_task(*task_call_args, **task_call_kwargs)
