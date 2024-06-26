#!/bin/bash

# get the directory of the script
DIR=$(dirname "$0")

# navigate to your Django project directory
cd $DIR

# activate the environment, assume venv is the same directory as the script
source $DIR/venv/bin/activate

usage() {
  echo "Usage: $0 [-m (make migrations)] [-a (apply migrations)] [-s (start server)]"
  exit 1
}

make_migrations=false
apply_migrations=false
start_server=false
all_options=false

while getopts "mash" opt; do
  case $opt in
    m)
      make_migrations=true
      ;;
    a)
      apply_migrations=true
      ;;
    s)
      start_server=true
      ;;
    h)
      usage
      ;;
  esac
done

if $make_migrations; then
  echo "Making migrations..."
  python manage.py makemigrations
fi

if $apply_migrations; then
  echo "Applying migrations..."
  python manage.py migrate
fi

if $start_server; then
  echo "Starting server..."
  python manage.py runserver
fi

# If no options are provided, run all
if [ $OPTIND -eq 1 ]; then
    # make the migrations
    python manage.py makemigrations
    # apply the migrations
    python manage.py migrate
    # run the Django server
    python manage.py runserver
fi

