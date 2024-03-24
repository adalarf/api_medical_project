from rest_framework import serializers
from .models import Doctor, SubjectInfo, CopyrightInfo, Patient


class DoctorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'patronymic', 'password', 'email')


class DoctorLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('email', 'password')
        extra_kwargs = {
            'email': {'validators': []}}


class BaseDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'patronymic', 'email')


class SubjectInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectInfo
        fields = ('subject_name', 'subject_text')


class SubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectInfo
        fields = ('subject_name', )


class CopyrightInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightInfo
        fields = ('copyright_text',)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('patient_test_id',)