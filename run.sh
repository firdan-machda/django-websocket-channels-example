#!/bin/bash

# get the directory of the script
DIR=$(dirname "$0")

# navigate to your Django project directory
cd $DIR

# activate the environment, assume venv is the same directory as the script
source $DIR/venv/bin/activate


# run the Django server
python manage.py runserver