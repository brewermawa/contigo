from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('pacientes/', views.patient_list, name='patient_list'),
    path('pacientes/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('pacientes/<int:pk>/comentario/', views.patient_comment_add, name='patient_comment_add'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)