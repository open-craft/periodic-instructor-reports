"""
Register signal receivers to listen on PeriodicReportSchedule changes.
"""

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django_celery_beat.models import PeriodicTask
from periodic_instructor_reports.models import PeriodicReportSchedule


# pylint: disable=unused-argument
@receiver(post_save, sender=PeriodicReportSchedule)
def create_or_update_related_periodic_task(
    sender, instance: PeriodicReportSchedule, *args, **kwargs
) -> None:
    """
    Create or update a `PeriodicTask` based on the `PeriodicReportSchedule`.

    When a `PeriodicReportSchedule` is created or updated, ensure the corresponding `PeriodicTask`
    is created or adjusted as well. The only argument of the `PeriodicTask` is the saved model
    instance's ID. This way the periodic task wrapper and the `PeriodicReportSchedule` are highly
    extensible.
    """

    # Get the celery task by ID if exists or create an "empty" task
    celery_task = (
        PeriodicTask.objects.get(id=instance.celery_task.id)
        if instance.celery_task
        else PeriodicTask()
    )

    # Override the celery task arguments
    celery_task.name = instance.task.name
    celery_task.task = "periodic_instructor_reports.tasks.periodic_task_wrapper"
    celery_task.interval = instance.interval
    celery_task.args = [instance.id]
    celery_task.save()

    # If the celery task was not set before, set it
    if not instance.celery_task:
        instance.celery_task = celery_task
        instance.save()


# pylint: disable=unused-argument
@receiver(pre_delete, sender=PeriodicReportSchedule)
def delete_related_periodic_task(
    sender, instance: PeriodicReportSchedule, *args, **kwargs
):
    """
    Delete the related celery task to not leave dangling references behind.
    """

    instance.celery_task.delete()
