from django.shortcuts import render, get_object_or_404, redirect
from .models import VolleyPlayer
from .forms import PlayerForm


def player_list(request):
    players = VolleyPlayer.objects.all()
    return render(request, 'player_list.html', {'players': players})


def player_detail(request, pk):
    player = get_object_or_404(VolleyPlayer, pk=pk)
    return render(request, 'player_detail.html', {'player': player})


def player_add(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_list')
    else:
        form = PlayerForm()
    return render(request, 'player_form.html', {'form': form, 'title': 'Add Player'})


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


def player_delete(request, pk):
    player = get_object_or_404(VolleyPlayer, pk=pk)
    if request.method == 'POST':
        player.delete()
        return redirect('player_list')
    return render(request, 'player_confirm_delete.html', {'player': player})
