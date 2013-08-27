web: newrelic-admin run-program gunicorn -c gunicorn.py.ini wsgi:application
scheduler: python manage.py celery worker --loglevel=debug -B -E --maxtasksperchild=1000
worker: python manage.py celery worker --loglevel=info -E --maxtasksperchild=1000
