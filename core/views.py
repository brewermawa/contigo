from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    DiseaseFormSet,
    FamilyFormSet,
    MedicationFormSet,
    AddressForm,
    PatientCommentForm,
    PatientForm,
)
from .models import Address, Companion, Patient, Visit, CompanionSchedule


@login_required
def dashboard(request):
    today = timezone.localdate()

    visitas_hoy = Visit.objects.filter(
        date=today
    ).select_related('patient', 'companion__user').order_by('start_time')

    visitas_activas = Visit.objects.filter(
        status=Visit.Status.SCHEDULED
    ).count()

    visitas_completadas = Visit.objects.filter(
        date=today,
        status=Visit.Status.COMPLETED
    ).count()

    proximas_visitas = Visit.objects.filter(
        date__gt=today,
        status__in=[Visit.Status.PENDING, Visit.Status.SCHEDULED]
    ).select_related('patient', 'companion__user').order_by('date', 'start_time')[:8]

    alertas = []
    for v in visitas_hoy:
        if v.status == Visit.Status.PENDING:
            alertas.append(
                f"{v.patient.first_name} {v.patient.last_name} — "
                f"visita sin confirmar ({v.start_time.strftime('%H:%M')})"
            )

    context = {
        'visitas_hoy': visitas_hoy,
        'visitas_activas': visitas_activas,
        'visitas_completadas': visitas_completadas,
        'proximas_visitas': proximas_visitas,
        'total_pacientes': Patient.objects.filter(active=True).count(),
        'total_acompanantes': Companion.objects.count(),
        'acompanantes': Companion.objects.select_related('user').all(),
        'alertas': alertas,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def patient_list(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', 'active')
    patients = Patient.objects.select_related('address').order_by('last_name', 'first_name')

    if status == 'active':
        patients = patients.filter(active=True)
    elif status == 'inactive':
        patients = patients.filter(active=False)

    if query:
        for term in query.split():
            patients = patients.filter(
                Q(first_name__icontains=term) | Q(last_name__icontains=term)
            )

    context = {'patients': patients, 'query': query, 'status': status}

    if request.headers.get('HX-Request'):
        return render(request, 'core/patient_list_partial.html', context)
    return render(request, 'core/patient_list.html', context)


@login_required
@require_POST
def patient_toggle_active(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.active = not patient.active
    patient.save(update_fields=['active'])
    messages.success(
        request,
        f"Paciente {'activado' if patient.active else 'desactivado'} correctamente."
    )
    return redirect('patient_detail', pk=patient.pk)


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(
        Patient.objects.select_related('address').prefetch_related(
            'diseases', 'medications', 'family', 'comments__user'
        ),
        pk=pk
    )
    return render(request, 'core/patient_detail.html', {
        'patient': patient,
        'form': PatientCommentForm(),
    })


@login_required
def patient_comment_add(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.patient = patient
            comment.user = request.user
            comment.save()
    return render(request, 'core/patient_comments_partial.html', {
        'patient': patient,
        'form': PatientCommentForm(),
    })


@login_required
def patient_form(request, pk=None):
    patient = get_object_or_404(Patient, pk=pk) if pk else None
    address = Address.objects.filter(patient=patient).first() if patient else None

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        address_form = AddressForm(request.POST, instance=address)
        disease_fs = DiseaseFormSet(request.POST, instance=patient)
        medication_fs = MedicationFormSet(request.POST, instance=patient)
        family_fs = FamilyFormSet(request.POST, instance=patient)

        # Lista (no generador) para que todos se validen y muestren sus errores
        all_valid = all([
            form.is_valid(), address_form.is_valid(),
            disease_fs.is_valid(), medication_fs.is_valid(), family_fs.is_valid(),
        ])

        if all_valid:
            with transaction.atomic():
                patient = form.save()
                address = address_form.save(commit=False)
                address.patient = patient
                address.save()
                for fs in (disease_fs, medication_fs, family_fs):
                    fs.instance = patient
                    fs.save()
            messages.success(request, "Paciente guardado correctamente.")
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
        address_form = AddressForm(instance=address)
        disease_fs = DiseaseFormSet(instance=patient)
        medication_fs = MedicationFormSet(instance=patient)
        family_fs = FamilyFormSet(instance=patient)

    return render(request, 'core/patient_form.html', {
        'patient': patient,
        'form': form,
        'address_form': address_form,
        'disease_fs': disease_fs,
        'medication_fs': medication_fs,
        'family_fs': family_fs,
    })


@login_required
def companion_list(request):
    query = request.GET.get('q', '')
    companions = Companion.objects.select_related('user').order_by(
        'user__last_name', 'user__first_name'
    )

    if query:
        for term in query.split():
            companions = companions.filter(
                Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term)
            )

    context = {'companions': companions, 'query': query}

    if request.headers.get('HX-Request'):
        return render(request, 'core/companion_list_partial.html', context)
    return render(request, 'core/companion_list.html', context)


@login_required
def companion_detail(request, pk):
    companion = get_object_or_404(
        Companion.objects.select_related('user').prefetch_related('schedules'),
        pk=pk
    )

    schedule_by_day = {s.weekday: s for s in companion.schedules.all()}
    week = [
        {'name': label, 'schedule': schedule_by_day.get(value)}
        for value, label in CompanionSchedule.Weekday.choices
    ]

    upcoming_visits = companion.visits.filter(
        date__gte=timezone.localdate(),
        status__in=[Visit.Status.PENDING, Visit.Status.SCHEDULED],
    ).select_related('patient').order_by('date', 'start_time')[:5]

    return render(request, 'core/companion_detail.html', {
        'companion': companion,
        'week': week,
        'upcoming_visits': upcoming_visits,
        'preferred_patients': companion.preferred_patients.filter(active=True),
    })