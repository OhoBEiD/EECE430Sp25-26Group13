import json

from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required, self_player_or_role
from accounts.permissions import can_record_stats
from accounts.querysets import players_for
from accounts.roles import Role, role_of

from players.models import VolleyPlayer

from .forms import StatsForm
from .models import PlayerStats
from attendance.models import Attendance
from feedback.models import Feedback
from lineups.models import LineupSlot
from injuries.models import Injury
from django.utils import timezone


ALL_AUTHED = (Role.PLAYER, Role.COACH, Role.MANAGER, Role.SCOUT, Role.ADMIN)
VIEW_ANYONE = (Role.COACH, Role.MANAGER, Role.SCOUT, Role.ADMIN)
RECORDERS = (Role.COACH, Role.MANAGER, Role.ADMIN)
DELETERS = (Role.MANAGER, Role.ADMIN)


@role_required(*ALL_AUTHED)
def analytics_select(request):
    players = players_for(request.user).order_by('name')
    if role_of(request.user) == Role.PLAYER:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.linked_player_id:
            players = players.filter(pk=profile.linked_player_id)
        else:
            players = players.none()
    return render(request, 'analytics/select_player.html', {'players': players})


@self_player_or_role(*VIEW_ANYONE, player_pk_kwarg='player_pk')
def analytics_dashboard(request, player_pk):
    player = get_object_or_404(VolleyPlayer, pk=player_pk)
    if not players_for(request.user).filter(pk=player.pk).exists():
        raise Http404
    all_stats = PlayerStats.objects.filter(player=player).order_by('date_recorded')
    latest_stats = all_stats.order_by('-date_recorded').first()
    previous_stats = all_stats.order_by('-date_recorded')[1] if all_stats.count() > 1 else None
    recent_stats = all_stats.order_by('-date_recorded')[:5]

    stats_json = json.dumps([{
        'date': s.date_recorded.strftime('%b %d'),
        'serve': s.serve_accuracy,
        'spike': s.spike_success,
        'block': s.block_rate,
        'dig': s.dig_success,
        'set': s.set_accuracy,
        'receive': s.receive_rating,
        'overall': s.overall_score,
    } for s in all_stats])

    diffs = {}
    if latest_stats and previous_stats:
        diffs = {
            'serve': latest_stats.serve_accuracy - previous_stats.serve_accuracy,
            'spike': latest_stats.spike_success - previous_stats.spike_success,
            'block': latest_stats.block_rate - previous_stats.block_rate,
            'dig': latest_stats.dig_success - previous_stats.dig_success,
            'set': latest_stats.set_accuracy - previous_stats.set_accuracy,
            'receive': latest_stats.receive_rating - previous_stats.receive_rating,
        }

    today = timezone.now().date()
    from datetime import timedelta
    thirty_days_ago = today - timedelta(days=30)

    # Attendance (last 30 days)
    total_att = Attendance.objects.filter(player=player, event__date__gte=thirty_days_ago).count()
    attendance_pct_30d = None
    if total_att > 0:
        attended = Attendance.objects.filter(player=player, event__date__gte=thirty_days_ago, status__in=['present', 'late']).count()
        attendance_pct_30d = int((attended / total_att) * 100)

    # Recent Feedback
    recent_feedback = Feedback.objects.filter(player=player).order_by('-created_at')[:3]

    # Active Injuries
    active_injuries = Injury.objects.filter(player=player, status='Active').order_by('-date_reported')

    context = {
        'player': player,
        'latest_stats': latest_stats,
        'previous_stats': previous_stats,
        'all_stats': all_stats,
        'recent_stats': recent_stats,
        'stats_json': stats_json,
        'overall_score': latest_stats.overall_score if latest_stats else None,
        'diffs': diffs,
        'attendance_pct_30d': attendance_pct_30d,
        'recent_feedback': recent_feedback,
        'active_injuries': active_injuries,
    }
    return render(request, 'analytics/dashboard.html', context)


@role_required(*RECORDERS)
def record_stats(request, player_pk):
    player = get_object_or_404(VolleyPlayer, pk=player_pk)
    if not can_record_stats(request.user, player):
        raise PermissionDenied
    if request.method == 'POST':
        form = StatsForm(request.POST)
        if form.is_valid():
            stats = form.save(commit=False)
            stats.player = player
            stats.recorded_by = request.user
            stats.save()
            return redirect('analytics_dashboard', player_pk=player.pk)
    else:
        form = StatsForm()
    return render(request, 'analytics/record_stats.html', {
        'form': form,
        'player': player,
    })


@role_required(*DELETERS)
def stats_delete(request, pk):
    stat = get_object_or_404(PlayerStats, pk=pk)
    player_pk = stat.player.pk
    if request.method == 'POST':
        stat.delete()
        return redirect('analytics_dashboard', player_pk=player_pk)
    return render(request, 'analytics/stats_confirm_delete.html', {
        'stat': stat,
    })
