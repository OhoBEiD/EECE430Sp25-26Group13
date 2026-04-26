from datetime import timedelta

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from injuries.models import Injury
from teams.models import Event

from .decorators import role_required
from .forms import RoleAssignmentForm
from .querysets import injuries_for, stats_for
from .roles import Role


@role_required(Role.PLAYER, Role.COACH, Role.MANAGER, Role.SCOUT, Role.ADMIN)
def me_view(request):
    profile = getattr(request.user, 'profile', None)
    linked = profile.linked_player if profile else None
    today = timezone.now().date()
    horizon = today + timedelta(days=14)
    own_events = []
    own_injuries = []
    recent_stats = []
    if linked is not None:
        if linked.team_id is not None:
            own_events = list(
                Event.objects.filter(team_id=linked.team_id, date__gte=today, date__lte=horizon)
                .order_by('date', 'start_time')[:5]
            )
        own_injuries = list(injuries_for(request.user).order_by('-date_reported'))
        recent_stats = list(stats_for(request.user).order_by('-date_recorded')[:5])
    return render(request, 'accounts/me.html', {
        'profile': profile,
        'own_events': own_events,
        'own_injuries': own_injuries,
        'recent_stats': recent_stats,
    })


@role_required(Role.COACH, Role.ADMIN)
def coach_landing(request):
    today = timezone.now().date()
    horizon = today + timedelta(days=14)
    coached = list(request.user.coached_teams.all())
    summaries = []
    for team in coached:
        summaries.append({
            'team': team,
            'roster': list(team.players.all().order_by('name')),
            'active_injuries': list(
                Injury.objects.filter(player__team=team, status='Active')
                .select_related('player').order_by('-date_reported')[:5]
            ),
            'upcoming_events': list(
                team.events.filter(date__gte=today, date__lte=horizon)
                .order_by('date', 'start_time')[:5]
            ),
        })
    return render(request, 'accounts/coach_landing.html', {
        'team_summaries': summaries,
    })


@role_required(Role.ADMIN)
def admin_user_list(request):
    users = (
        User.objects.select_related('profile')
        .prefetch_related('coached_teams')
        .order_by('username')
    )
    return render(request, 'accounts/admin_user_list.html', {'users': users})


@role_required(Role.ADMIN)
def admin_user_edit_role(request, pk):
    user_obj = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    profile = user_obj.profile
    if request.method == 'POST':
        form = RoleAssignmentForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('admin_user_list')
    else:
        form = RoleAssignmentForm(instance=profile)
    return render(request, 'accounts/admin_user_edit.html', {
        'form': form,
        'user_obj': user_obj,
    })
