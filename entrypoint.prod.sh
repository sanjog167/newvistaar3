#!/bin/sh
#python manage.py collectstatic -v 2 --noinput
#python manage.py migrate
#python manage.py runserver 0.0.0.0:80
gunicorn --bind :8000 vistaar.wsgi
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec "$@"