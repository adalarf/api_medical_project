from rest_framework import serializers
from .models import Doctor, SubjectInfo, CopyrightInfo, Patient, Test, Indicator, Graphic


class DoctorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ("first_name", "last_name", "patronymic", "password", "email")


class DoctorLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ("email", "password")
        extra_kwargs = {
            "email": {"validators": []}}


class BaseDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ("first_name", "last_name", "patronymic", "email")


class SubjectInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectInfo
        fields = ("subject_name", "subject_text")


class SubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectInfo
        fields = ("id", "subject_name", )


class CopyrightInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightInfo
        fields = ("copyright_text",)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ("diagnosis_date", "chemoterapy",)


class PatientInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("id", "first_name", "last_name", "patronymic", "birth_date",)


class PatientOperationSerializer(serializers.ModelSerializer):
    diagnosis = serializers.CharField(required=False)
    diagnosis_comment = serializers.CharField(required=False)
    diagnosis_date = serializers.DateField(required=False)
    operation_comment = serializers.CharField(required=False)
    chemoterapy = serializers.CharField(required=False)
    chemoterapy_comment = serializers.CharField(required=False)

    class Meta:
        model = Patient
        fields = ("diagnosis", "diagnosis_comment", "diagnosis_date",  "operation_comment", "chemoterapy",
                  "chemoterapy_comment")


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        exclude = ("id",)

    def create(self, validated_data):
        return Indicator.objects.create(**validated_data)


class TestNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ("name",)


class ConclusionSerializer(serializers.ModelSerializer):
    conclusion = serializers.CharField(required=False)
    recommendations = serializers.CharField(required=False)

    class Meta:
        model = Test
        fields = ("conclusion", "recommendations",)


class ChangeRefsSerializer(serializers.Serializer):
    cd19_cd4_min = serializers.FloatField(required=False)
    lymf_cd19_min = serializers.FloatField(required=False)
    neu_lymf_min = serializers.FloatField(required=False)
    cd19_cd8_min = serializers.FloatField(required=False)

    cd19_cd4_max = serializers.FloatField(required=False)
    lymf_cd19_max = serializers.FloatField(required=False)
    neu_lymf_max = serializers.FloatField(required=False)
    cd19_cd8_max = serializers.FloatField(required=False)


class SearchPatientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    patronymic = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True, default="", input_formats=["%Y-%m-%d", ""])

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["birth_date"] == "1900-01-01":
            ret["birth_date"] = ""
        return ret

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "patronymic", "birth_date",)


class GraphicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graphic
        fields = ("graphic",)
