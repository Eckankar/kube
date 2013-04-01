from collections import defaultdict
from operator import attrgetter
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.datastructures import SortedDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Timekeeper.models import Session, Avg5

def index(request):
    last_session = Session.objects.order_by('-date')[:1]

    return render_to_response("front.html", RequestContext(request, {
        'active_tab': 'frontpage',
        'latest_session': last_session,
    } ))

def meetings(request):
    sessions = Session.objects.order_by('-date')
    paginator = Paginator(sessions, 1)

    page = request.GET.get('page')
    try:
        sessions = paginator.page(page)
    except PageNotAnInteger:
        sessions = paginator.page(1)
    except EmptyPage:
        sessions = paginator.page(paginator.num_pages)

    return render_to_response("meetings.html", RequestContext(request, {
        'active_tab': 'meetings',
        'sessions': sessions,
        } ))

def userpage(request, id):
    user = get_object_or_404(User, pk=id)
    times = Avg5.objects.filter(user=user).order_by('-session__date')

    puzzles = defaultdict(list)
    for time in times:
        puzzles[time.puzzle].append(time)

    sortedpuzzles = SortedDict()
    for pn in sorted(puzzles.keys(), key=attrgetter('name')):
        sortedpuzzles[pn] = puzzles[pn]

    return render_to_response("userpage.html", RequestContext(request, {
        'profile': user,
        'puzzles': sortedpuzzles,
    } ))

