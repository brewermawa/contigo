from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Pacientes
    path('pacientes/', views.patient_list, name='patient_list'),
    path('pacientes/nuevo/', views.patient_form, name='patient_create'),
    path('pacientes/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('pacientes/<int:pk>/editar/', views.patient_form, name='patient_edit'),
    path('pacientes/<int:pk>/comentario/', views.patient_comment_add, name='patient_comment_add'),
    path('pacientes/<int:pk>/activo/', views.patient_toggle_active, name='patient_toggle_active'),
    path('acompanantes/', views.companion_list, name='companion_list'),
    path('acompanantes/<int:pk>/', views.companion_detail, name='companion_detail'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)