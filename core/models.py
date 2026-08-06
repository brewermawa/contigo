from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Companion(models.Model):
    class Meta:
        verbose_name = "Acompañante"
        verbose_name_plural = "Acompañantes"

    phone_validator = RegexValidator(
        regex=r"^\d{10}$",
        message="El número de teléfono debe tener exactamente 10 dígitos numéricos."
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="acompanante", verbose_name="Usuario")
    phone = models.CharField(max_length=10, validators=[phone_validator], verbose_name="Teléfono")
    picture = models.ImageField(upload_to='acompanantes/', verbose_name="Foto")

    def __str__(self):
        return f"{self.user.get_full_name()}"
    
    def formatted_phone(self):
        return f"({self.phone[:2]}){self.phone[2:6]}-{self.phone[6:]}"
    

class Patient(models.Model):
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    phone_validator = RegexValidator(
        regex=r"^\d{10}$",
        message="El número de teléfono debe tener exactamente 10 dígitos numéricos."
    )

    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    phone = models.CharField(max_length=10, validators=[phone_validator], verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo electrónico")
    birth_date = models.DateField(verbose_name="Fecha de nacimiento")
    picture = models.ImageField(upload_to='pacientes/', verbose_name="Foto")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def formatted_phone(self):
        return f"({self.phone[:2]}){self.phone[2:6]}-{self.phone[6:]}"
    

class PatientComment(models.Model):
    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['-created_at']

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="comments", verbose_name="Paciente")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="patient_comments", verbose_name="Usuario")
    comment = models.TextField(verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    def __str__(self):
        return f"{self.patient} — {self.created_at:%d/%m/%Y}"


class Address(models.Model):
    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="address", verbose_name="Paciente")
    street = models.CharField(max_length=200, verbose_name="Calle")
    ext_number = models.CharField(max_length=20, verbose_name="Número exterior")
    int_number = models.CharField(max_length=20, blank=True, verbose_name="Número interior")
    neighborhood = models.CharField(max_length=100, verbose_name="Colonia")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Estado")
    zip_code = models.CharField(max_length=5, verbose_name="Código postal")
    comment = models.TextField(blank=True, verbose_name="Comentarios")

    def __str__(self):
        return f"{self.street} {self.ext_number}, {self.neighborhood}, {self.city}"
    

class Disease(models.Model):
    class Meta:
        verbose_name = "Enfermedad"
        verbose_name_plural = "Enfermedades"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="diseases", verbose_name="Paciente")
    name = models.CharField(max_length=200, verbose_name="Enfermedad")
    comment = models.TextField(blank=True, verbose_name="Comentarios")

    def __str__(self):
        return f"{self.name} - {self.patient}"
    

class Medication(models.Model):
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medications", verbose_name="Paciente")
    name = models.CharField(max_length=200, verbose_name="Medicamento")
    dosage = models.CharField(max_length=100, verbose_name="Dosis")
    frequency = models.CharField(max_length=100, verbose_name="Frecuencia")
    active = models.BooleanField(default=True, verbose_name="Activo")
    comment = models.TextField(blank=True, verbose_name="Comentarios")

    def __str__(self):
        return f"{self.name} - {self.patient}"
    

class Family(models.Model):
    class Meta:
        verbose_name = "Familiar"
        verbose_name_plural = "Familiares"

    class Relationship(models.TextChoices):
        CHILD = 'child', 'Hijo(a)'
        SPOUSE = 'spouse', 'Esposo(a)'
        SIBLING = 'sibling', 'Hermano(a)'
        OTHER = 'other', 'Otro'

    phone_validator = RegexValidator(
        regex=r"^\d{10}$",
        message="El número de teléfono debe tener exactamente 10 dígitos numéricos."
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="family", verbose_name="Paciente")
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    phone = models.CharField(max_length=10, validators=[phone_validator], verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo electrónico")
    relationship = models.CharField(max_length=10, choices=Relationship.choices, verbose_name="Parentesco")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_relationship_display()})"

    def formatted_phone(self):
        return f"({self.phone[:2]}){self.phone[2:6]}-{self.phone[6:]}"
    

class Visit(models.Model):
    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ['-date', '-start_time']

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        SCHEDULED = 'scheduled', 'Programada'
        COMPLETED = 'completed', 'Completada'
        CANCELLED = 'cancelled', 'Cancelada'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits", verbose_name="Paciente")
    companion = models.ForeignKey(Companion, on_delete=models.CASCADE, related_name="visits", verbose_name="Acompañante")
    date = models.DateField(verbose_name="Fecha")
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Notas")

    def __str__(self):
        return f"{self.patient} - {self.companion} - {self.date}"
    


class PhysicalActivity(models.Model):
    class Meta:
        verbose_name = "Actividad física"
        verbose_name_plural = "Actividades físicas"

    name = models.CharField(max_length=200, verbose_name="Actividad")

    def __str__(self):
        return self.name


class VisitReport(models.Model):
    class Meta:
        verbose_name = "Reporte de visita"
        verbose_name_plural = "Reportes de visita"

    class Mood(models.TextChoices):
        VERY_HAPPY = 'very_happy', 'Muy alegre'
        HAPPY = 'happy', 'Alegre'
        CALM = 'calm', 'Tranquilo'
        MELANCHOLIC = 'melancholic', 'Melancólico'
        TIRED = 'tired', 'Cansado'
        UNCOMFORTABLE = 'uncomfortable', 'Incómodo'

    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name="report", verbose_name="Visita")

    mood = models.CharField(max_length=15, choices=Mood.choices, verbose_name="Estado de ánimo")
    
    # Signos vitales
    systolic_pressure = models.PositiveIntegerField(verbose_name="Presión sistólica")
    diastolic_pressure = models.PositiveIntegerField(verbose_name="Presión diastólica")
    heart_rate = models.PositiveIntegerField(verbose_name="Frecuencia cardíaca")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Temperatura")
    oxygen_saturation = models.PositiveIntegerField(verbose_name="Saturación de oxígeno")
    glucose = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True, verbose_name="Glucosa")


    # Actividad física
    physical_activities = models.ManyToManyField(PhysicalActivity, blank=True, verbose_name="Actividades físicas")
    physical_activity_comment = models.TextField(blank=True, verbose_name="Comentarios de actividad física")

    # Medicamentos
    medications_taken = models.ManyToManyField(Medication, blank=True, verbose_name="Medicamentos tomados")

    # Estimulación cognitiva
    cognitive_stimulation = models.BooleanField(default=False, verbose_name="Estimulación cognitiva")

    # Notas generales
    notes = models.TextField(blank=True, verbose_name="Notas generales")

    def __str__(self):
        return f"Reporte - {self.visit}"
    
    def blood_pressure(self):
        return f"{self.systolic_pressure}/{self.diastolic_pressure}"
    

class CompanionSchedule(models.Model):
    class Meta:
        verbose_name = "Agenda de acompañante"
        verbose_name_plural = "Agenda de acompañantes"
        unique_together = ['companion', 'weekday']

    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Lunes'
        TUESDAY = 1, 'Martes'
        WEDNESDAY = 2, 'Miércoles'
        THURSDAY = 3, 'Jueves'
        FRIDAY = 4, 'Viernes'
        SATURDAY = 5, 'Sábado'
        SUNDAY = 6, 'Domingo'

    companion = models.ForeignKey(Companion, on_delete=models.CASCADE, related_name="schedules", verbose_name="Acompañante")
    weekday = models.IntegerField(choices=Weekday.choices, verbose_name="Día de la semana")
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")

    def __str__(self):
        return f"{self.companion} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"