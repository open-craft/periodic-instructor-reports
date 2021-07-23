# Periodic Instructor Reports

This edX Django Plugin App makes possible to run qualified instructor report tasks periodically.

An instructor report is qualified if, and only if, can be scheduled by Celery (ie. it is decorated by `@task`) and using or passing the keyword arguments to the task that will be called.

## Installation

First you'll need to install the django app.

``` sh
sudo -E -u edxapp env "PATH=$PATH" /edx/app/edxapp/venvs/edxapp/bin/python -m pip install -e git+https://gitlab.com/opencraft/client/esme-learning/periodic-instructor-reports.git@gabor/initial-implementation#egg=periodic-instructor-reports
```

After doing so, you will need to change the `/edx/etc/lms.yml` to add `django_celery_beat` to additionally installed apps and set `CELERYBEAT_SCHEDULER` to the `DatabaseScheduler` to run tasks periodically.

``` yaml
#/edx/etc/lms.yml
ADDL_INSTALLED_APPS:
- django_celery_beat

CELERYBEAT_SCHEDULER: "django_celery_beat.schedulers:DatabaseScheduler"
```

After all is set restart the `lms` devstack.

## Run in devstack

Devstack won't run the Celery message broker by default. To start the redis broker, run `make dev.up.redis`.

``` sh
# In the devstack repository
make dev.up.redis
```

After the redis broker started, start the workers within the lms shell seen below.

``` sh
# Activate the virtualenv
source /edx/app/edxapp/edxapp_env

# Run paver
paver celery

# Or optionally, in the lms shell, start the worker manually
# DJANGO_SETTINGS_MODULE=lms.envs.devstack_with_worker celery worker --beat --app=lms.celery:APP -Q edx.core.default
```

## Run tests manually

```
PYTHONPATH=$(pwd) DJANGO_SETTINGS_MODULE=test_settings django-admin test
```
