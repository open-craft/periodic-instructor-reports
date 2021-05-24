# Generated by Django 2.2.20 on 2021-04-28 03:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.encoder
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicReportTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the task. Used for representation purposes on the Admin UI.', max_length=254)),
                ('path', models.CharField(help_text='Python path of the task need to be called periodically. Example:\n        lms.djangoapps.instructor_task.api.submit_calculate_students_features_csv', max_length=254)),
                ('requires_request', models.BooleanField(default=False, help_text='Indicates if the task requires a requests as a first parameter.')),
            ],
            options={
                'verbose_name': 'Periodic report task',
                'verbose_name_plural': 'Periodic report tasks',
                'unique_together': {('name', 'path')},
            },
        ),
        migrations.CreateModel(
            name='PeriodicReportSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_ids', jsonfield.fields.JSONField(default=[], dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, help_text='List of course and CCX course IDs to run the reports against.', load_kwargs={})),
                ('arguments', jsonfield.fields.JSONField(blank=True, default=[], dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, help_text='List of arguments passed to the task.', load_kwargs={}, null=True)),
                ('keyword_arguments', jsonfield.fields.JSONField(blank=True, default={}, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, help_text='Keyword arguments passed to the task.', load_kwargs={}, null=True)),
                ('include_ccx', models.BooleanField(default=False, help_text="If set to True, the listed courses' related ccx courses will be included in\n        the report generation.\n        ")),
                ('only_ccx', models.BooleanField(default=False, help_text='Run the task execution only against CCX courses.')),
                ('upload_folder_structure', models.CharField(choices=[('regular', 'regular'), ('by_date', 'by_date')], default='regular', help_text='Define the folder structure during upload.', max_length=32)),
                ('celery_task', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.PeriodicTask')),
                ('interval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.IntervalSchedule')),
                ('owner', models.ForeignKey(help_text='The user who created the periodic report task.', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='periodic_instructor_reports.PeriodicReportTask')),
            ],
            options={
                'verbose_name': 'Periodic report schedule',
                'verbose_name_plural': 'Periodic report schedules',
            },
        ),
    ]
