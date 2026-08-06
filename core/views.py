from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Companion, Patient, Visit
from .forms import PatientCommentForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

@login_required
def dashboard(request):
    today = timezone.now().date()

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

    total_pacientes = Patient.objects.count()
    total_acompanantes = Companion.objects.count()

    alertas = []
    for v in visitas_hoy:
        if v.status == Visit.Status.PENDING:
            alertas.append(
                f"{v.patient.first_name} {v.patient.last_name} — visita sin confirmar ({v.start_time.strftime('%H:%M')})"
            )

    context = {
        'visitas_hoy': visitas_hoy,
        'visitas_activas': visitas_activas,
        'visitas_completadas': visitas_completadas,
        'proximas_visitas': proximas_visitas,
        'total_pacientes': total_pacientes,
        'total_acompanantes': total_acompanantes,
        'acompanantes': Companion.objects.select_related('user').all(),
        'alertas': alertas,
    }

    return render(request, 'core/dashboard.html', context)


@login_required
def patient_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by('last_name', 'first_name')

    print(f"Total pacientes: {patients.count()}")  # debug
    print(f"Query: '{query}'")  # debug

    if query:
        patients = patients.filter(
            first_name__icontains=query
        ) | patients.filter(
            last_name__icontains=query
        )

    if request.headers.get('HX-Request'):
        return render(request, 'core/patient_list_partial.html', {'patients': patients, 'query': query})

    return render(request, 'core/patient_list.html', {'patients': patients, 'query': query})




@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(
        Patient.objects.prefetch_related(
            'diseases',
            'medications',
            'family',
            'address'
        ),
        pk=pk
    )
    return render(request, 'core/patient_detail.html', {'patient': patient})


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