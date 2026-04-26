from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notes = request.user.notifications.all()[:50]
    return render(request, 'notifications/list.html', {'notes': notes})


@login_required
@require_POST
def mark_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, user=request.user)
    note.read = True
    note.save(update_fields=['read'])
    return redirect(note.link or 'notification_list')


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(read=False).update(read=True)
    return redirect('notification_list')
