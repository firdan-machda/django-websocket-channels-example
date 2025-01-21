#!/bin/bash

# get the directory of the script
DIR=$(dirname "$0")

# navigate to your Django project directory
if [ -d "$DIR" ]; then
    cd $DIR
else
    echo "Directory does not exist"
    exit 1
fi

# check if venv exists
if [ ! -d "$DIR/venv" ]; then
    # create virtualenv 
    python3.11 -m venv venv
fi

# activate the environment, assume venv is the same directory as the script
source $DIR/venv/bin/activate

# install the requirements
pip install -r requirements.txt

# run the Django server
python manage.py runserver