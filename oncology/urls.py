from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.DoctorSignupView.as_view()),
    path("login/", views.DoctorLoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("profile/", views.DoctorProfileView.as_view()),

    path("add-subject-info/", views.SubjectInfoPostView.as_view()),
    path("subject-info/<int:pk>/", views.SubjectInfoView.as_view()),
    path("subject-info/", views.SubjectListView.as_view()),
    path("copyright-info/", views.CopyrightInfoView.as_view(), kwargs={"pk": 1}),

    path("create-patient/", views.PatientCreationView.as_view()),
    path("edit-patient/<int:pk>/", views.PatientEditView.as_view()),

    path("indicator/", views.IndicatorView.as_view()),

    path("patient-test/", views.PatientTestsView.as_view()),
    path("patient-test-edit/<int:pk>/", views.PatientTestsEditView.as_view()),
    path("patient-operation-info/<int:pk>/", views.OperationInfoView.as_view()),
    path("patients-info/", views.PatientInfoView.as_view()),

    path("graphic/<int:pk>/", views.GraphicView.as_view()),

    path("test-patient/<int:pk>/", views.TestsPatientView.as_view()),

    path("analysis-comparison/<int:pk>/", views.AnalysisComparisonView.as_view()),
    path("patient-analysis/<int:pk>/", views.PatientAnalysisView.as_view()),

    path("search-patient/", views.SearchPatientView.as_view()),

    path("conclusion/<int:pk>/", views.ConclusionView.as_view()),
    path("change-refs/<int:pk>/", views.ChangeRefsView.as_view()),
]
