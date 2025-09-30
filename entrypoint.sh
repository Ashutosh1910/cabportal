#!/bin/sh

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

#python manage.py rename apogee2022 apogee2025

# Make migrations and migrate the database.
echo "Making migrations and migrating the database. "
#python manage.py makemigrations main --noinput 
#python manage.py makemigrations registrations --noinput
#python manage.py makemigrations regsoft --noinput
#python manage.py makemigrations wallet --noinput
#python manage.py makemigrations aarohan --noinput
#python manage.py makemigrations ticketadmin --noinput
#python manage.py makemigrations tickets_manager --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput 
python manage.py collectstatic --noinput

exec "$@"
