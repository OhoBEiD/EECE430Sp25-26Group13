import csv

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import VolleyPlayer
from .forms import PlayerForm


def player_list(request):
    q = request.GET.get('q', '').strip()
    qs = VolleyPlayer.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'player_list.html', {
        'players': page_obj,
        'page_obj': page_obj,
        'q': q,
    })


def player_detail(request, pk):
    player = get_object_or_404(VolleyPlayer, pk=pk)
    return render(request, 'player_detail.html', {'player': player})


@login_required
def player_add(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_list')
    else:
        form = PlayerForm()
    return render(request, 'player_form.html', {'form': form, 'title': 'Add Player'})


@login_required
def player_edit(request, pk):
    player = get_object_or_404(VolleyPlayer, pk=pk)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player_list')
    else:
        form = PlayerForm(instance=player)
    return render(request, 'player_form.html', {'form': form, 'title': 'Edit Player'})


@login_required
def player_delete(request, pk):
    player = get_object_or_404(VolleyPlayer, pk=pk)
    if request.method == 'POST':
        player.delete()
        return redirect('player_list')
    return render(request, 'player_confirm_delete.html', {'player': player})


def player_export_csv(request):
    q = request.GET.get('q', '').strip()
    qs = VolleyPlayer.objects.select_related('team').all()
    if q:
        qs = qs.filter(name__icontains=q)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="players.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Position', 'Team', 'Date joined', 'Salary', 'Contact'])
    for p in qs:
        writer.writerow([
            p.id,
            p.name,
            p.position,
            p.team.name if p.team else '',
            p.date_joined.isoformat() if p.date_joined else '',
            p.salary,
            p.contact_person,
        ])
    return response
