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
    upcoming_events = team.events.filter(date__gte=timezone.now().date())
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'players': players,
        'upcoming_events': upcoming_events,
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
    events_by_date = {}
    for event in qs:
        events_by_date.setdefault(event.date, []).append(event)
    return render(request, 'teams/schedule.html', {
        'events_by_date': events_by_date,
        'has_events': qs.exists(),
    })
