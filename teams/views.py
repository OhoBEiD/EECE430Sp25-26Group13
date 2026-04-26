from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required, team_coach_required
from accounts.querysets import teams_for
from accounts.roles import Role

from .forms import EventForm, TeamForm
from .models import Event, Team


def team_list(request):
    teams = teams_for(request.user).annotate(player_count=Count('players'))
    return render(request, 'teams/team_list.html', {'teams': teams})


def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not teams_for(request.user).filter(pk=team.pk).exists():
        raise Http404
    players = team.players.all()
    upcoming_events = team.events.filter(date__gte=timezone.now().date()).order_by('date')
    recent_past_events = team.events.filter(date__lt=timezone.now().date()).order_by('-date')[:5]
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'players': players,
        'upcoming_events': upcoming_events,
        'recent_past_events': recent_past_events,
    })

from lineups.models import LineupSlot

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not teams_for(request.user).filter(pk=event.team_id).exists():
        raise Http404
    team = event.team
    players = team.players.all()
    attendance_map = {a.player_id: a for a in event.attendance.all()}
    
    lineups_map = {s.position: s.player_id for s in event.lineup_slots.all()}
    lineup_data = []
    for pos_code, pos_label in LineupSlot.POSITION_CHOICES:
        lineup_data.append({'pos_code': pos_code, 'pos_label': pos_label, 'assigned_player_id': lineups_map.get(pos_code)})

    from attendance.models import EventRSVP
    rsvps_map = {r.player_id: r for r in event.rsvps.all()}
    player_rsvp = None
    is_player = False
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == Role.PLAYER:
        is_player = True
        if profile.linked_player_id:
            player_rsvp = rsvps_map.get(profile.linked_player_id)
        
    return render(request, 'teams/event_detail.html', {
        'event': event,
        'team': team,
        'players': players,
        'attendance_map': attendance_map,
        'lineup_data': lineup_data,
        'rsvps_map': rsvps_map,
        'player_rsvp': player_rsvp,
        'is_player': is_player,
    })



@role_required(Role.MANAGER, Role.ADMIN)
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamForm(user=request.user)
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create Team'})


@team_coach_required('pk')
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm(instance=team, user=request.user)
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Edit Team'})


@role_required(Role.MANAGER, Role.ADMIN)
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        team.delete()
        return redirect('team_list')
    return render(request, 'teams/team_confirm_delete.html', {'team': team})


@team_coach_required('team_pk')
def event_create(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.team = team
            event.save()
            return redirect('team_detail', pk=team.pk)
    else:
        form = EventForm()
    return render(request, 'teams/event_form.html', {'form': form, 'team': team})


@role_required(Role.COACH, Role.MANAGER, Role.ADMIN)
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not teams_for(request.user).filter(pk=event.team_id).exists():
        raise PermissionDenied
    team_pk = event.team.pk
    if request.method == 'POST':
        event.delete()
        return redirect('team_detail', pk=team_pk)
    return render(request, 'teams/event_confirm_delete.html', {'event': event})


def schedule_view(request):
    qs = Event.objects.filter(date__gte=timezone.now().date()).select_related('team')
    visible_team_ids = list(teams_for(request.user).values_list('id', flat=True))
    qs = qs.filter(team_id__in=visible_team_ids)
    
    import json
    from django.urls import reverse
    
    events_json = []
    for event in qs:
        # Theme mapping
        bg_color = 'rgba(52, 199, 89, 0.15)'
        border_color = 'rgba(52, 199, 89, 0.3)'
        text_color = '#34c759'
        if event.event_type == 'Game':
            bg_color = 'rgba(255, 59, 48, 0.15)'
            border_color = 'rgba(255, 59, 48, 0.3)'
            text_color = '#ff3b30'
        elif event.event_type == 'Tournament':
            bg_color = 'rgba(88, 86, 214, 0.15)'
            border_color = 'rgba(88, 86, 214, 0.3)'
            text_color = '#afadff'

        events_json.append({
            'title': f"{event.team.name}: {event.title}",
            'start': f"{event.date.isoformat()}T{event.start_time.isoformat()}",
            'end': f"{event.date.isoformat()}T{event.end_time.isoformat()}",
            'url': reverse('event_detail', args=[event.pk]),
            'backgroundColor': bg_color,
            'borderColor': border_color,
            'textColor': text_color,
        })

    return render(request, 'teams/schedule.html', {
        'events_json_str': json.dumps(events_json),
        'has_events': qs.exists(),
    })
