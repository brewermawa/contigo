from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Companion, CompanionSchedule, Patient, Address, Disease,
    Medication, Family, Visit, PhysicalActivity, VisitReport, PatientComment,
)


# Companion
class CompanionScheduleInline(admin.TabularInline):
    model = CompanionSchedule
    extra = 1


class CompanionInline(admin.StackedInline):
    model = Companion
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [CompanionInline]


class CompanionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'phone']
    inlines = [CompanionScheduleInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Companion, CompanionAdmin)


# Patient
class AddressInline(admin.StackedInline):
    model = Address
    can_delete = False


class DiseaseInline(admin.TabularInline):
    model = Disease
    extra = 1


class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 1


class FamilyInline(admin.TabularInline):
    model = Family
    extra = 1



class PatientCommentInline(admin.TabularInline):
    model = PatientComment
    extra = 1
    readonly_fields = ['created_at']


class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email', 'active']
    list_filter = ['active']
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [AddressInline, DiseaseInline, MedicationInline, FamilyInline, PatientCommentInline]



class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email']
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [AddressInline, DiseaseInline, MedicationInline, FamilyInline, PatientCommentInline]


admin.site.register(Patient, PatientAdmin)


# Visit
class VisitReportInline(admin.StackedInline):
    model = VisitReport
    can_delete = False


class VisitAdmin(admin.ModelAdmin):
    list_display = ['patient', 'companion', 'date', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'date', 'companion']
    search_fields = ['patient__first_name', 'patient__last_name']
    inlines = [VisitReportInline]


admin.site.register(Visit, VisitAdmin)


# PhysicalActivity
admin.site.register(PhysicalActivity)