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


from attendance.models import Attendance

@role_required(Role.PLAYER, Role.COACH, Role.MANAGER, Role.SCOUT, Role.ADMIN)
def me_view(request):
    profile = getattr(request.user, 'profile', None)
    linked = profile.linked_player if profile else None
    today = timezone.now().date()
    horizon = today + timedelta(days=14)
    own_events = []
    own_injuries = []
    recent_stats = []
    attendance_pct = None
    own_lineups = []
    
    if linked is not None:
        if linked.team_id is not None:
            own_events = list(
                Event.objects.filter(team_id=linked.team_id, date__gte=today, date__lte=horizon)
                .order_by('date', 'start_time')[:5]
            )
        own_injuries = list(injuries_for(request.user).order_by('-date_reported'))
        recent_stats = list(stats_for(request.user).order_by('-date_recorded')[:5])
        
        total_att = Attendance.objects.filter(player=linked).count()
        if total_att > 0:
            attended = Attendance.objects.filter(player=linked, status__in=['present', 'late']).count()
            attendance_pct = int((attended / total_att) * 100)
            
        from lineups.models import LineupSlot
        own_lineups = list(
            LineupSlot.objects.filter(player=linked, event__date__gte=today)
            .select_related('event')
            .order_by('event__date')
        )

    return render(request, 'accounts/me.html', {
        'profile': profile,
        'own_events': own_events,
        'own_injuries': own_injuries,
        'recent_stats': recent_stats,
        'attendance_pct': attendance_pct,
        'own_lineups': own_lineups,
    })


@role_required(Role.COACH, Role.ADMIN)
def coach_landing(request):
    today = timezone.now().date()
    horizon = today + timedelta(days=14)
    coached = list(request.user.coached_teams.all())
    summaries = []
    for team in coached:
        thirty_days_ago = today - timedelta(days=30)
        team_att = Attendance.objects.filter(event__team=team, event__date__gte=thirty_days_ago)
        total_att = team_att.count()
        attendance_pct = None
        if total_att > 0:
            attended = team_att.filter(status__in=['present', 'late']).count()
            attendance_pct = int((attended / total_att) * 100)

        summaries.append({
            'team': team,
            'roster': list(team.players.all().order_by('name')),
            'attendance_pct': attendance_pct,
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
