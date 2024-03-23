from django.contrib import admin
from .models import Doctor, Patient, PatientTests, SubjectInfo, Test, Analysis, Indicator, CopyrightInfo


admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(PatientTests)
admin.site.register(Test)
admin.site.register(Analysis)
admin.site.register(Indicator)
admin.site.register(SubjectInfo)
admin.site.register(CopyrightInfo)
