#!/bin/sh

python manage.py db upgrade
python app.py
