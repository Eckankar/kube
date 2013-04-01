from collections import defaultdict
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from Timekeeper.models import Avg5, Session
from django.utils import simplejson

def user_api(request, id):
    user = get_object_or_404(User, pk=id)
    times = Avg5.objects.filter(user=user).order_by('session__date')

    puzzles = defaultdict(list)
    for time in times:
        puzzles[time.puzzle].append(time)

    response = {
        'chartData': {
            'chart': { 'type': 'line' },
            'credits': { 'enabled': False },
            'series': [],
            'title': { 'text': str(user) },
            'xAxis': {
                'categories': [s.notes for s in Session.objects.all()]
            }
        }
    }
    for puzzle, times in puzzles.items():
        series = {
            'name': puzzle.name,
            'data': [],
        }

        for time in times:
            series['data'].append([time.session.id - 1, float(time.avg().timestamp)])

        response['chartData']['series'].append(series)

    return HttpResponse(simplejson.dumps(response), content_type="application/json")


