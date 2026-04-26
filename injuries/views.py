from datetime import date

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.permissions import can_view_injury
from accounts.querysets import injuries_for
from accounts.roles import Role

from .forms import InjuryForm
from .models import Injury


INJURY_STATUS_CHOICES = ['Active', 'Recovering', 'Cleared']

VIEWERS = (Role.PLAYER, Role.COACH, Role.MANAGER, Role.SCOUT, Role.ADMIN)
WRITERS = (Role.COACH, Role.MANAGER, Role.ADMIN)
DELETERS = (Role.MANAGER, Role.ADMIN)


@role_required(*VIEWERS)
def injury_list(request):
    all_injuries = injuries_for(request.user).select_related('player')
    active_count = all_injuries.filter(status='Active').count()
    recovered_count = all_injuries.filter(status='Cleared').count()

    cleared_with_dates = all_injuries.filter(status='Cleared', expected_return__isnull=False)
    if cleared_with_dates.exists():
        total_days = 0
        count = 0
        for injury in cleared_with_dates:
            days = (injury.expected_return - injury.date_reported).days
            if days > 0:
                total_days += days
                count += 1
        avg_recovery = round(total_days / count) if count > 0 else None
    else:
        avg_recovery = None

    status = request.GET.get('status', '').strip()
    if status in INJURY_STATUS_CHOICES:
        injuries = all_injuries.filter(status=status)
    else:
        injuries = all_injuries
        status = ''

    return render(request, 'injuries/injury_list.html', {
        'injuries': injuries,
        'active_count': active_count,
        'recovered_count': recovered_count,
        'avg_recovery': avg_recovery,
        'status': status,
        'status_choices': INJURY_STATUS_CHOICES,
    })


@role_required(*VIEWERS)
def injury_detail(request, pk):
    injury = get_object_or_404(Injury.objects.select_related('player'), pk=pk)
    if not can_view_injury(request.user, injury):
        raise PermissionDenied

    recovery_percent = None
    if injury.date_reported and injury.expected_return:
        total_days = (injury.expected_return - injury.date_reported).days
        if total_days > 0:
            elapsed_days = (date.today() - injury.date_reported).days
            recovery_percent = min(round((elapsed_days / total_days) * 100), 100)

    return render(request, 'injuries/injury_detail.html', {
        'injury': injury,
        'recovery_percent': recovery_percent,
    })


@role_required(*WRITERS)
def injury_create(request):
    if request.method == 'POST':
        form = InjuryForm(request.POST, user=request.user)
        if form.is_valid():
            injury = form.save(commit=False)
            if not injury.reported_by_user_id:
                injury.reported_by_user = request.user
            injury.save()
            return redirect('injury_list')
    else:
        form = InjuryForm(user=request.user)
    return render(request, 'injuries/injury_form.html', {
        'form': form,
        'title': 'Log New Injury',
    })


@role_required(*WRITERS)
def injury_edit(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    if not can_view_injury(request.user, injury):
        raise PermissionDenied
    if request.method == 'POST':
        form = InjuryForm(request.POST, instance=injury, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('injury_detail', pk=injury.pk)
    else:
        form = InjuryForm(instance=injury, user=request.user)
    return render(request, 'injuries/injury_form.html', {
        'form': form,
        'title': 'Edit Injury',
    })


@role_required(*DELETERS)
def injury_delete(request, pk):
    injury = get_object_or_404(Injury.objects.select_related('player'), pk=pk)
    if request.method == 'POST':
        injury.delete()
        return redirect('injury_list')
    return render(request, 'injuries/injury_confirm_delete.html', {
        'injury': injury,
    })
