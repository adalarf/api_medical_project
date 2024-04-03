from rest_framework import serializers
from .models import Doctor, SubjectInfo, CopyrightInfo, Patient, PatientTests, Test, Analysis, Indicator, Graphic
from datetime import datetime


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
        fields = ('id', 'subject_name', )


class CopyrightInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopyrightInfo
        fields = ('copyright_text',)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        # exclude = ('id', )
        fields = '__all__'


class PatientInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'first_name', 'last_name', 'patronymic', 'birth_date',)


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        exclude = ('id',)

    def create(self, validated_data):
        return Indicator.objects.create(**validated_data)

class IndicatorNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ('name',)

class AnalysisSerializer(serializers.ModelSerializer):
    indicator_id = IndicatorNameSerializer()

    class Meta:
        model = Analysis
        fields = ['value', 'indicator_id']

class TestSerializer(serializers.ModelSerializer):
    analysis_id = AnalysisSerializer(many=True)

    class Meta:
        model = Test
        fields = ['analysis_id', 'name']

    def create(self, validated_data):
        analysis_data = validated_data.pop('analysis_id')

        test = Test.objects.create(**validated_data)
        test.save()

        for analysis in analysis_data:
            indicator_data = analysis.pop('indicator_id')
            indicator = Indicator.objects.get(name=indicator_data['name'])
            analysis_obj = Analysis.objects.create(indicator_id=indicator, **analysis)
            analysis_obj.save()
            test.analysis_id.add(analysis_obj)
            test.save()
        return test

class PatientTestsSerializer(serializers.ModelSerializer):
    test_id = TestSerializer(many=True)

    class Meta:
        model = PatientTests
        fields = ['test_id', 'analysis_date',]


#     def create(self, validated_data):
#         request = self.context.get('request')  
#         doctor_id = request.user if request and request.user else None  

#         tests_data = validated_data.pop('test_id')
#         current_time = datetime.now()

#         patient_test = PatientTests.objects.create(doctor_id=doctor_id, created_at=current_time, updated_at=current_time, **validated_data) 

#         for test_data in tests_data:
#             analyses_data = test_data.pop('analysis_id')
#             test = Test.objects.create(**test_data)

#             for analysis_data in analyses_data:
#                 indicator_data = analysis_data.pop('indicator_id')
#                 # indicator, created = Indicator.objects.get_or_create(name=indicator_data['name'], defaults={'interval_min': 0, 'interval_max': 0, 'unit': ''})  # замените значения по умолчанию на вашу логику
#                 indicator = Indicator.objects.get(name=indicator_data['name'])
#                 analysis = Analysis.objects.create(indicator_id=indicator, **analysis_data)
#                 # test.analysis_id.add(analysis)
#                 test.analysis_id.set([analysis]) 

#             patient_test.test_id.add(test)

#         return patient_test


class GraphicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graphic
        fields = ('graphic',)