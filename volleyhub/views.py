from datetime import timedelta

from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone

from accounts.querysets import injuries_for, players_for, stats_for, teams_for
from accounts.roles import VISITOR, Role, role_of
from injuries.models import Injury
from players.models import VolleyPlayer
from teams.models import Event, Team


def dashboard(request):
    role = role_of(request.user)
    today = timezone.now().date()
    horizon = today + timedelta(days=7)

    if role == VISITOR:
        return _dashboard_visitor(request, today, horizon)
    if role == Role.PLAYER:
        return _dashboard_player(request, today, horizon)
    if role == Role.COACH:
        return _dashboard_coach(request, today, horizon)
    if role == Role.SCOUT:
        return _dashboard_scout(request, today, horizon)
    if role == Role.ADMIN:
        return _dashboard_admin(request, today, horizon)
    return _dashboard_manager(request, today, horizon)


def _public_aggregates(today, horizon):
    return {
        'player_count': VolleyPlayer.objects.count(),
        'team_count': Team.objects.count(),
        'upcoming_event_count': Event.objects.filter(date__gte=today, date__lte=horizon).count(),
    }


def _upcoming(qs, today, horizon, limit=5):
    return list(
        qs.filter(date__gte=today, date__lte=horizon)
        .select_related('team')
        .order_by('date', 'start_time')[:limit]
    )


def _dashboard_visitor(request, today, horizon):
    context = _public_aggregates(today, horizon)
    context['upcoming_events'] = _upcoming(Event.objects, today, horizon)
    return render(request, 'dashboard_visitor.html', context)


def _dashboard_player(request, today, horizon):
    profile = getattr(request.user, 'profile', None)
    linked = profile.linked_player if profile else None
    own_events = []
    own_injuries = []
    recent_stats = []
    open_injury_count = 0
    if linked is not None:
        events_qs = Event.objects.filter(team_id=linked.team_id) if linked.team_id else Event.objects.none()
        own_events = _upcoming(events_qs, today, horizon)
        if own_events:
            from attendance.models import EventRSVP
            rsvp_map = {
                r.event_id: r.status
                for r in EventRSVP.objects.filter(player_id=linked.pk, event_id__in=[e.pk for e in own_events])
            }
            for ev in own_events:
                ev.current_rsvp_status = rsvp_map.get(ev.pk)
        own_injuries = list(injuries_for(request.user).order_by('-date_reported'))
        open_injury_count = sum(1 for i in own_injuries if i.status != 'Cleared')
        recent_stats = list(stats_for(request.user).order_by('-date_recorded')[:3])
    context = {
        'own_events': own_events,
        'own_injuries': own_injuries,
        'open_injury_count': open_injury_count,
        'recent_stats': recent_stats,
    }
    return render(request, 'dashboard_player.html', context)


def _dashboard_coach(request, today, horizon):
    coached = list(teams_for(request.user))
    team_summaries = []
    for team in coached:
        team_summaries.append({
            'team': team,
            'player_count': players_for(request.user).filter(team=team).count(),
            'active_injury_count': injuries_for(request.user).filter(
                player__team=team, status='Active'
            ).count(),
            'upcoming_events': _upcoming(Event.objects.filter(team=team), today, horizon, limit=3),
        })
    context = {
        'team_summaries': team_summaries,
        'open_injury_count': injuries_for(request.user).filter(status='Active').count(),
    }
    return render(request, 'dashboard_coach.html', context)


def _dashboard_manager(request, today, horizon):
    context = _public_aggregates(today, horizon)
    context['active_injury_count'] = Injury.objects.filter(status='Active').count()
    context['upcoming_events'] = _upcoming(Event.objects, today, horizon)
    return render(request, 'dashboard_manager.html', context)


def _dashboard_scout(request, today, horizon):
    context = _public_aggregates(today, horizon)
    context['active_injury_count'] = Injury.objects.filter(status='Active').count()
    context['upcoming_events'] = _upcoming(Event.objects, today, horizon)
    return render(request, 'dashboard_scout.html', context)


def _dashboard_admin(request, today, horizon):
    context = _public_aggregates(today, horizon)
    context['active_injury_count'] = Injury.objects.filter(status='Active').count()
    context['upcoming_events'] = _upcoming(Event.objects, today, horizon)
    context['user_count'] = User.objects.count()
    return render(request, 'dashboard_admin.html', context)
