web: python manage.py db upgrade && gunicorn app:app
worker: python -m celery -A tasks worker --loglevel INFO
