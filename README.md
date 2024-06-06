# Django Channel Example
Simple chat app to demonstrate WebSocket

## Setup
- Install requirements\
`pip install -r requirements.txt`

- Migrate\
`python manage.py migrate`

- Run\
`python manage.py runserver`

## Styling
styling use tailwind css please refer to documentation for more explanation;
1. install tailwind with `npm -D tailwindcss`
1. To compile the style style do `npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css`
1. To make tailwindcss watch the changes add `--watch` like so `npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch`

## Access chat page through API
* chat;
http://localhost:8000/chat
or
http://localhost:8000/chat/(roomname)
* livechat; http://localhost:8000/chat/live/(roomname)