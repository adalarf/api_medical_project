from rest_framework import serializers
from .models import Doctor


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