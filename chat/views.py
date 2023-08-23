from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'chat.html')

def room(request, room_name):
    return render(request, "room/chat.html", {"room_name": room_name})