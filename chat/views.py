from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ChatThread, ChatMessage
from accounts.querysets import teams_for
from accounts.roles import role_of, Role

@login_required
def chat_index(request):
    teams = teams_for(request.user)
    visible_team_ids = list(teams.values_list('id', flat=True))
    
    user_role = role_of(request.user)
    is_staff = user_role in [Role.COACH, Role.MANAGER, Role.ADMIN]
    
    threads = ChatThread.objects.filter(
        Q(team_id__in=visible_team_ids) | Q(event__team_id__in=visible_team_ids)
    )
    if not is_staff:
        threads = threads.exclude(thread_type='team_staff')
        
    return render(request, 'chat/index.html', {'threads': threads})

@login_required
def chat_room(request, thread_id):
    thread = get_object_or_404(ChatThread, id=thread_id)
    teams = teams_for(request.user)
    user_role = role_of(request.user)
    is_staff = user_role in [Role.COACH, Role.MANAGER, Role.ADMIN]
    
    if thread.team_id and thread.team_id not in teams.values_list('id', flat=True):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if thread.event_id and thread.event.team_id not in teams.values_list('id', flat=True):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if thread.thread_type == 'team_staff' and not is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
        
    messages = thread.messages.select_related('sender').order_by('timestamp')
    
    return render(request, 'chat/room.html', {
        'thread': thread,
        'messages': messages,
    })
