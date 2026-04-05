from datetime import date

from django.db.models import Avg, F
from django.shortcuts import render, get_object_or_404, redirect

from .models import Injury
from .forms import InjuryForm


def injury_list(request):
    injuries = Injury.objects.select_related('player').all()
    active_count = injuries.filter(status='Active').count()
    recovered_count = injuries.filter(status='Cleared').count()

    # Average recovery days for cleared injuries that have both dates
    cleared_with_dates = injuries.filter(
        status='Cleared',
        expected_return__isnull=False,
    )
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

    return render(request, 'injuries/injury_list.html', {
        'injuries': injuries,
        'active_count': active_count,
        'recovered_count': recovered_count,
        'avg_recovery': avg_recovery,
    })


def injury_detail(request, pk):
    injury = get_object_or_404(Injury.objects.select_related('player'), pk=pk)

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


def injury_create(request):
    if request.method == 'POST':
        form = InjuryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('injury_list')
    else:
        form = InjuryForm()
    return render(request, 'injuries/injury_form.html', {
        'form': form,
        'title': 'Log New Injury',
    })


def injury_edit(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    if request.method == 'POST':
        form = InjuryForm(request.POST, instance=injury)
        if form.is_valid():
            form.save()
            return redirect('injury_detail', pk=injury.pk)
    else:
        form = InjuryForm(instance=injury)
    return render(request, 'injuries/injury_form.html', {
        'form': form,
        'title': 'Edit Injury',
    })


def injury_delete(request, pk):
    injury = get_object_or_404(Injury.objects.select_related('player'), pk=pk)
    if request.method == 'POST':
        injury.delete()
        return redirect('injury_list')
    return render(request, 'injuries/injury_confirm_delete.html', {
        'injury': injury,
    })
