from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.utils import timezone

from teams.models import Event
from .models import Attendance
from accounts.permissions import can_edit_team

@require_POST
def attendance_submit(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if not can_edit_team(request.user, event.team):
        raise PermissionDenied
    
    for player in event.team.players.all():
        status = request.POST.get(f'status_{player.pk}')
        notes = request.POST.get(f'notes_{player.pk}', '').strip()
        if status:
            Attendance.objects.update_or_create(
                event=event,
                player=player,
                defaults={
                    'status': status,
                    'notes': notes,
                    'marked_by': request.user if request.user.is_authenticated else None,
                    'marked_at': timezone.now()
                }
            )
    return redirect('event_detail', pk=event.pk)

@require_POST
def rsvp_submit(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.linked_player:
        raise PermissionDenied
        
    player = profile.linked_player
    if player.team_id != event.team_id:
        raise PermissionDenied
        
    status = request.POST.get('status')
    reason = request.POST.get('reason', '').strip()
    
    from .models import EventRSVP
    if status in dict(EventRSVP.STATUS_CHOICES):
        EventRSVP.objects.update_or_create(
            event=event,
            player=player,
            defaults={
                'status': status,
                'reason': reason
            }
        )
    return redirect('event_detail', pk=event.pk)
