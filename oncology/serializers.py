from rest_framework import serializers
from .models import Doctor, SubjectInfo, CopyrightInfo


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


class CopyrightInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightInfo
        fields = ('copyright_text',)