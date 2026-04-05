from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.utils import timezone

from .models import Team, Event
from .forms import TeamForm, EventForm


def team_list(request):
    teams = Team.objects.annotate(player_count=Count('players')).all()
    return render(request, 'teams/team_list.html', {'teams': teams})


def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    players = team.players.all()
    upcoming_events = team.events.filter(date__gte=timezone.now().date())
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'players': players,
        'upcoming_events': upcoming_events,
    })


def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamForm()
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create Team'})


def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm(instance=team)
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Edit Team'})


def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        team.delete()
        return redirect('team_list')
    return render(request, 'teams/team_confirm_delete.html', {'team': team})


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


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    team_pk = event.team.pk
    if request.method == 'POST':
        event.delete()
        return redirect('team_detail', pk=team_pk)
    return render(request, 'teams/event_confirm_delete.html', {'event': event})


def schedule_view(request):
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now().date()
    ).select_related('team')
    # Group events by date
    events_by_date = {}
    for event in upcoming_events:
        date_key = event.date
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)
    return render(request, 'teams/schedule.html', {
        'events_by_date': events_by_date,
        'has_events': upcoming_events.exists(),
    })
