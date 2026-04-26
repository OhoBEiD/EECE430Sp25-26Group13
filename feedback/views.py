from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from teams.models import Event
from .models import Feedback
from accounts.permissions import can_edit_team

@require_POST
def feedback_submit(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if not can_edit_team(request.user, event.team):
        raise PermissionDenied
    
    for player in event.team.players.all():
        body = request.POST.get(f'feedback_body_{player.pk}', '').strip()
        if body:
            # simple implementation: overwrite or create a feedback
            feedback, created = Feedback.objects.update_or_create(
                event=event,
                player=player,
                defaults={
                    'body': body,
                    'coach': request.user if request.user.is_authenticated else None
                }
            )
    return redirect('event_detail', pk=event.pk)
