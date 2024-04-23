"""
URL configuration for oncology_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from oncology import views
from .yasg import urlpatterns as doc_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/signup/', views.DoctorSignupView.as_view()),
    path('api/v1/login/', views.DoctorLoginView.as_view()),
    path('api/v1/logout/', views.LogoutView.as_view()),
    path('api/v1/profile/', views.DoctorProfileView.as_view()),

    path('api/v1/add-subject-info/', views.SubjectInfoPostView.as_view()),
    path('api/v1/subject-info/<int:pk>/', views.SubjectInfoView.as_view()),
    path('api/v1/subject-info/', views.SubjectListView.as_view()),
    path('api/v1/copyright-info/', views.CopyrightInfoView.as_view(), kwargs={'pk': 1}),

    path('api/v1/create-patient/', views.PatientCreationView.as_view()),
    path('api/v1/edit-patient/<int:pk>/', views.PatientEditView.as_view()),

    path('api/v1/indicator/', views.IndicatorView.as_view()),

    path('api/v1/patient-test/', views.PatientTestsView.as_view()),

    path('api/v1/patient-test-edit/<int:pk>/', views.PatientTestsEditView.as_view()),

    path('api/v1/graphic-create/', views.GraphicCreateView.as_view()),
    path('api/v1/graphic/<int:pk>/', views.GraphicView.as_view()),

    path('api/v1/patients-info/', views.PatientInfoView.as_view()),

    path('api/v1/test-patient/<int:pk>/', views.TestsPatientView.as_view()),

    path('api/v1/patient-analysis/<int:pk>/', views.PatientAnalysisView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += doc_urls
