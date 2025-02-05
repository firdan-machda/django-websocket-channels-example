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

activate_venv(){
    # activate the environment, assume venv is the same directory as the script
    source $DIR/venv/bin/activate
}

# check if venv exists
create_venv(){
    if [ ! -d "$DIR/venv" ]; then
        # create virtualenv 
        python3.11 -m venv venv
        echo "venv created"
    else
        echo "venv already exists"
    fi
}


install_requirements(){
    # install the requirements
    pip install -r requirements.txt
}

migrate_database(){
    # pull the latest changes
    git pull
    # migrate the database
    python manage.py migrate
}

run_server(){
    # run the Django server
    python manage.py runserver
}

# Parse command-line options
while getopts "cimr" opt; do
    case $opt in
        c)
            create_venv
            ;;
        i)
            activate_venv
            install_requirements
            ;;
        m)
            activate_venv
            migrate_database
            ;;
        r)
            activate_venv
            run_server
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

# If no options were provided, show usage
if [ $OPTIND -eq 1 ]; then
    echo "Usage: $0 [-c] [-i] [-m] [-r]"
    echo "  -c  Create virtual environment"
    echo "  -i  Install requirements"
    echo "  -m  Pull and Migrate database"
    echo "  -r  Run Django server"
    exit 1
fi