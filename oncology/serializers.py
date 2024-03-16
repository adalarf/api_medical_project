from rest_framework import serializers
from .models import Doctor, SubjectInfo, CopyrightInfo


class DoctorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'patronymic', 'password', 'login', 'email')


class DoctorLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('login', 'password')
        extra_kwargs = {
            'login': {'validators': []}}


class BaseDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'patronymic', 'login', 'email')


class SubjectInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectInfo
        fields = ('subject_name', 'subject_text')


class CopyrightInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightInfo
        fields = ('copyright_text',)