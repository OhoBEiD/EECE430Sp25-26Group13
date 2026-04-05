import json
from django.shortcuts import render, get_object_or_404, redirect
from players.models import VolleyPlayer
from .models import PlayerStats
from .forms import StatsForm


def analytics_select(request):
    players = VolleyPlayer.objects.all()
    return render(request, 'analytics/select_player.html', {'players': players})


def analytics_dashboard(request, player_pk):
    player = get_object_or_404(VolleyPlayer, pk=player_pk)
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

    # Calculate differences for trend arrows
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

    context = {
        'player': player,
        'latest_stats': latest_stats,
        'previous_stats': previous_stats,
        'all_stats': all_stats,
        'recent_stats': recent_stats,
        'stats_json': stats_json,
        'overall_score': latest_stats.overall_score if latest_stats else None,
        'diffs': diffs,
    }
    return render(request, 'analytics/dashboard.html', context)


def record_stats(request, player_pk):
    player = get_object_or_404(VolleyPlayer, pk=player_pk)
    if request.method == 'POST':
        form = StatsForm(request.POST)
        if form.is_valid():
            stats = form.save(commit=False)
            stats.player = player
            stats.save()
            return redirect('analytics_dashboard', player_pk=player.pk)
    else:
        form = StatsForm()
    return render(request, 'analytics/record_stats.html', {
        'form': form,
        'player': player,
    })


def stats_delete(request, pk):
    stat = get_object_or_404(PlayerStats, pk=pk)
    player_pk = stat.player.pk
    if request.method == 'POST':
        stat.delete()
        return redirect('analytics_dashboard', player_pk=player_pk)
    return render(request, 'analytics/stats_confirm_delete.html', {
        'stat': stat,
    })
