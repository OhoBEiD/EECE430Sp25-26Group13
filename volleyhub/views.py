from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from players.models import VolleyPlayer
from teams.models import Team, Event
from injuries.models import Injury


def dashboard(request):
    today = timezone.now().date()
    horizon = today + timedelta(days=7)

    upcoming_events = (
        Event.objects
        .filter(date__gte=today, date__lte=horizon)
        .select_related('team')
        .order_by('date', 'start_time')[:5]
    )

    context = {
        'player_count': VolleyPlayer.objects.count(),
        'team_count': Team.objects.count(),
        'active_injury_count': Injury.objects.filter(status='Active').count(),
        'upcoming_event_count': Event.objects.filter(date__gte=today, date__lte=horizon).count(),
        'upcoming_events': upcoming_events,
    }
    return render(request, 'dashboard.html', context)
