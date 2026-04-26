from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib import messages

from teams.models import Event
from .models import LineupSlot
from accounts.permissions import can_edit_team
from players.models import VolleyPlayer

@require_POST
def lineup_submit(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if not can_edit_team(request.user, event.team):
        raise PermissionDenied
    
    positions = ['SETTER', 'OH1', 'OH2', 'MB1', 'MB2', 'OPP', 'LIBERO']
    assigned_players = set()
    errors = []

    # Validation
    for pos in positions:
        player_id = request.POST.get(f'lineup_{pos}')
        if player_id:
            if player_id in assigned_players:
                errors.append(f"A player cannot be assigned multiple times.")
            assigned_players.add(player_id)
            
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect('event_detail', pk=event.pk)
        
    LineupSlot.objects.filter(event=event).delete()
    
    for pos in positions:
        player_id = request.POST.get(f'lineup_{pos}')
        if player_id:
            try:
                player = VolleyPlayer.objects.get(pk=player_id, team=event.team)
                slot = LineupSlot(event=event, position=pos, player=player)
                slot.clean()
                slot.save()
            except Exception as e:
                messages.error(request, str(e))
                
    return redirect('event_detail', pk=event.pk)
