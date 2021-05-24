from datetime import date

from unittest import TestCase
from unittest.mock import Mock, patch, call

from ccx_keys.locator import CCXLocator
from opaque_keys.edx.locator import CourseLocator
from periodic_instructor_reports.tasks import (
    create_fake_request,
    periodic_task_wrapper,
)


class TaskUtilsTestCase(TestCase):
    """
    Test task execution utility functions.
    """

    def test_create_fake_request(self):
        """
        Test creating a fake Django request object.
        """

        user = Mock()
        request = create_fake_request(user)
        self.assertEqual(request.user, user)
        self.assertEqual(request.META["SERVER_PORT"], 0)
        self.assertEqual(request.META["SERVER_NAME"], "localhost")
        self.assertEqual(request.META["REMOTE_ADDR"], "0.0.0.0")


class PeriodicTaskWrapperTestCase(TestCase):
    """
    Test periodic task execution wrapper.
    """

    course_id = "course-v1:test+course+2021_T1"
    course_locator = CourseLocator("test", "course", "2021_T1", None, None)

    ccx_course_id = "ccx-v1:edX+DemoX+Demo_Course+ccx@1"
    ccx_course_locator = CCXLocator.from_string(ccx_course_id)

    def get_mock_schedule(self, schedule_id: int, owner: object) -> object:
        """
        Helper function returning a mock schedule object.
        """

        mock_schedule = Mock()
        mock_schedule.id = schedule_id
        mock_schedule.include_ccx = False
        mock_schedule.only_ccx = False
        mock_schedule.owner = owner
        mock_schedule.course_ids = [self.course_id]
        mock_schedule.arguments = ["arg1", "arg2"]
        mock_schedule.keyword_arguments = {"kw1": 1, "kw2": 2}
        mock_schedule.task.requires_request = False
        mock_schedule.upload_folder_prefix = ""

        return mock_schedule

    @patch("periodic_instructor_reports.tasks.PeriodicReportSchedule")
    @patch("periodic_instructor_reports.tasks.get_function_from_path")
    def test_task_wrapper(self, mock_get_function, mock_schedules):
        """
        Test an expected periodic task execution.
        """

        owner = Mock()
        schedule_id = 1

        mock_report_task = Mock()
        mock_get_function.return_value = mock_report_task

        mock_schedule = self.get_mock_schedule(schedule_id, owner)
        mock_schedules.objects.get.return_value = mock_schedule

        periodic_task_wrapper(schedule_id)

        mock_report_task.assert_called_once_with(
            self.course_locator, "arg1", "arg2", kw1=1, kw2=2
        )

    @patch("periodic_instructor_reports.tasks.get_ccx_model")
    @patch("periodic_instructor_reports.tasks.PeriodicReportSchedule")
    @patch("periodic_instructor_reports.tasks.get_function_from_path")
    def test_task_wrapper_include_ccx(self, mock_get_function, mock_schedules, mock_ccx_model_getter):
        """
        Test the periodic reports should include CCX.
        """

        owner = Mock()
        schedule_id = 1

        mock_report_task = Mock()
        mock_get_function.return_value = mock_report_task

        mock_schedule = self.get_mock_schedule(schedule_id, owner)
        mock_schedule.include_ccx = True

        mock_schedules.objects.get.return_value = mock_schedule

        mock_ccx_course = Mock()
        mock_ccx_course.locator = self.ccx_course_locator
        mock_ccx_courses = [mock_ccx_course]

        mock_ccx_model_getter.return_value.objects.filter.return_value = mock_ccx_courses

        periodic_task_wrapper(schedule_id)

        mock_report_task.assert_has_calls([
            call(self.course_locator, "arg1", "arg2", kw1=1, kw2=2),
            call(self.ccx_course_locator, "arg1", "arg2", kw1=1, kw2=2),
        ])

    @patch("periodic_instructor_reports.tasks.get_ccx_model")
    @patch("periodic_instructor_reports.tasks.PeriodicReportSchedule")
    @patch("periodic_instructor_reports.tasks.get_function_from_path")
    def test_task_wrapper_include_only_ccx(self, mock_get_function, mock_schedules, mock_ccx_model_getter):
        """
        Test the periodic reports include only CCX.
        """

        owner = Mock()
        schedule_id = 1

        mock_report_task = Mock()
        mock_get_function.return_value = mock_report_task

        mock_schedule = self.get_mock_schedule(schedule_id, owner)
        mock_schedule.include_ccx = True
        mock_schedule.only_ccx = True

        mock_schedules.objects.get.return_value = mock_schedule

        mock_ccx_course = Mock()
        mock_ccx_course.locator = self.ccx_course_locator
        mock_ccx_courses = [mock_ccx_course]

        mock_ccx_model_getter.return_value.objects.filter.return_value = mock_ccx_courses

        periodic_task_wrapper(schedule_id)

        mock_report_task.assert_has_calls([
            call(self.ccx_course_locator, "arg1", "arg2", kw1=1, kw2=2),
        ])

    @patch("periodic_instructor_reports.tasks.PeriodicReportSchedule")
    @patch("periodic_instructor_reports.tasks.get_function_from_path")
    def test_task_wrapper_use_custom_folder_structure(self, mock_get_function, mock_schedules):
        """
        Test periodic reports will be uploaded to a date-based folder.
        """

        owner = Mock()
        schedule_id = 1

        mock_report_task = Mock()
        mock_get_function.return_value = mock_report_task

        mock_schedule = self.get_mock_schedule(schedule_id, owner)
        mock_schedule.upload_folder_structure = mock_schedules.STRUCTURE_BY_DATE

        mock_schedules.objects.get.return_value = mock_schedule

        periodic_task_wrapper(schedule_id)

        mock_report_task.assert_called_once_with(
            self.course_locator,
            "arg1",
            "arg2",
            kw1=1,
            kw2=2,
            upload_parent_dir=date.today().strftime("%Y/%m/%d"),
        )

    @patch("periodic_instructor_reports.tasks.PeriodicReportSchedule")
    @patch("periodic_instructor_reports.tasks.get_function_from_path")
    def test_task_wrapper_use_custom_folder_prefix(self, mock_get_function, mock_schedules):
        """
        Test periodic reports will be uploaded to a date-based folder.
        """

        owner = Mock()
        schedule_id = 1

        mock_report_task = Mock()
        mock_get_function.return_value = mock_report_task

        mock_schedule = self.get_mock_schedule(schedule_id, owner)
        mock_schedule.upload_folder_structure = mock_schedules.STRUCTURE_REGULAR
        mock_schedule.upload_folder_prefix = "test/"

        mock_schedules.objects.get.return_value = mock_schedule

        periodic_task_wrapper(schedule_id)

        mock_report_task.assert_called_once_with(
            self.course_locator,
            "arg1",
            "arg2",
            kw1=1,
            kw2=2,
            upload_parent_dir="{}".format(
                mock_schedule.upload_folder_prefix,
            ),
        )

    @patch("periodic_instructor_reports.tasks.PeriodicReportSchedule")
    @patch("periodic_instructor_reports.tasks.get_function_from_path")
    def test_task_wrapper_use_custom_folder_prefix(self, mock_get_function, mock_schedules):
        """
        Test periodic reports will be uploaded to a date-based folder.
        """

        owner = Mock()
        schedule_id = 1

        mock_report_task = Mock()
        mock_get_function.return_value = mock_report_task

        mock_schedule = self.get_mock_schedule(schedule_id, owner)
        mock_schedule.upload_folder_structure = mock_schedules.STRUCTURE_REGULAR
        mock_schedule.upload_folder_prefix = "test/"

        mock_schedules.objects.get.return_value = mock_schedule

        periodic_task_wrapper(schedule_id)

        mock_report_task.assert_called_once_with(
            self.course_locator,
            "arg1",
            "arg2",
            kw1=1,
            kw2=2,
            upload_parent_dir="{}".format(
                mock_schedule.upload_folder_prefix,
                date.today().strftime("%Y/%m/%d")
            ),
        )
