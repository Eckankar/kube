from django.shortcuts import render_to_response
from django.template.context import RequestContext
from Timekeeper.models import Session

def index(request):
    sessions = Session.objects.order_by('-date')

    return render_to_response("front.html", RequestContext(request, {
        'sessions': sessions,
    } ))