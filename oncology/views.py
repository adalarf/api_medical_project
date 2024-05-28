from django.conf import settings
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView,\
    ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import DoctorSignupSerializer, BaseDoctorSerializer, DoctorLoginSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Doctor, SubjectInfo, CopyrightInfo, Patient, Indicator, Test, Analysis, PatientTests, Graphic
from .serializers import SubjectInfoSerializer, CopyrightInfoSerializer, PatientSerializer, SubjectListSerializer,\
    PatientTestsSerializer, IndicatorSerializer, TestSerializer, GraphicSerializer, PatientInfoSerializer,\
    AnalysisSerializer, AnalysisWithReferentValuesSerializer, TestNameSerializer, SearchPatientSerializer,\
    ConclusionSerializer, ChangeRefsSerializer
from datetime import datetime
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import draw_hematological_research, draw_immune_status, draw_cytokine_status, draw_regeneration_type,\
    draw_regeneration_type1, get_refs, get_hematological_research_result, get_immune_status_result, get_cytokine_status_result, get_regeneration_type_result
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Avg
from decimal import Decimal
from .test_utils import change_hematological_refs, change_immune_refs, change_cytokine_refs, change_regeneration_refs


class DoctorSignupView(GenericAPIView):
    serializer_class = DoctorSignupSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = Doctor.objects.get(email=request.data['email'])
            user.set_password(request.data['password'])
            user.is_active = True
            user.save()
            token = Token.objects.create(user=user)
            return Response({
                'token': token.key,
                'user': user.id,
            })
        return Response(serializer.errors)


class DoctorLoginView(GenericAPIView):
    serializer_class = DoctorLoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            try:
                user = Doctor.objects.get(email=email)
            except Doctor.DoesNotExist:
                return Response({'error': 'Неверный логин или пароль'})

            if not user.check_password(password):
                return Response({'error': 'Неверный логин или пароль'})

            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': user.email})

        return Response(serializer.errors)


class LogoutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response('Вы вышли из акканта')


class DoctorProfileView(RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = BaseDoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SubjectInfoPostView(GenericAPIView):
    """
    Эндпоинт для создания Области применения
    subject_name - имя области применения
    subject_text - описание области применения
    """
    serializer_class = SubjectInfoSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SubjectInfoView(RetrieveUpdateDestroyAPIView):
    """
    Эндпоинт для вывода/редактирования/удаления Области применения<br>
    subject_name - имя области применения
    значения, хранящиеся в базе по умолчанию:
    oncology
    hematology
    surgery
    subject_text - описание области применения
    """
    queryset = SubjectInfo.objects.all()
    serializer_class = SubjectInfoSerializer


class SubjectListView(ListAPIView):
    """
    Эндпоинт для вывода имен областей применения
    """
    queryset = SubjectInfo.objects.all()
    serializer_class = SubjectListSerializer


class CopyrightInfoView(RetrieveUpdateDestroyAPIView):
    """
    Эндпоинт для вывода/редактирования/удаления Авторских прав
    copyright_text - описание Авторских прав
    """
    queryset = CopyrightInfo.objects.all()
    serializer_class = CopyrightInfoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = CopyrightInfo.objects.get(pk=kwargs['pk'])
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class PatientCreationView(CreateAPIView):
    """
    Создание пациента
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class PatientEditView(RetrieveUpdateDestroyAPIView):
    """
    Редактирование данных о пациенте
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class PatientInfoView(ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientInfoSerializer


class IndicatorView(CreateAPIView):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer


class TestsPatientView(APIView):
    """
    Эндпоинт для вывода информации об анализах пациента, где id - id пациента, вывод в виде:
        {
        "patient_tests": [
            {
                "analysis_date": "2024-03-24",
                "tests":[
                   {
                       "id": 1,
                       "name": "hematological_research"
                   },
                   {
                        "id": 2,
                        "name": "immune_status"
                   }
                ]
            }
       ]
    }
    """
    def get(self, request, pk):
        patient = Patient.objects.prefetch_related(
            Prefetch('patienttests_set', queryset=PatientTests.objects.prefetch_related('test_set'))
        ).get(pk=pk)

        data = {
            "patient_tests": []
        }

        for patient_test in patient.patienttests_set.all():
            patient_test_data = {
                "id": patient_test.id,
                "analysis_date": patient_test.analysis_date,
                "tests": []
            }

            for test in patient_test.test_set.all():
                patient_test_data["tests"].append({
                    "id": test.pk,
                    "name": test.name
                })

            data["patient_tests"].append(patient_test_data)

        return Response(data)



class PatientTestsView(APIView):
    """
    Эндпоинт для создания тестов пациента
    """
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['analysis_date', 'test', 'patient_id'],
        properties={
            'analysis_date': openapi.Schema(type=openapi.TYPE_STRING),
            'test': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'analysis': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'value': openapi.Schema(type=openapi.TYPE_STRING),
                                    'indicator_name': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            ),
            'patient_id': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ))
    def post(self, request):
        analysis_date = request.data['analysis_date']
        doctor_id = request.user
        current_time = datetime.now()
        created_at = current_time
        updated_at = current_time
        tests = request.data['test']
        patient = request.data['patient_id']
        try:
            patient_id = Patient.objects.get(id=patient)
        except Patient.DoesNotExist:
            raise NotFound('Пациент не найден')
        patient_test = PatientTests.objects.create(doctor_id=doctor_id, created_at=created_at, updated_at=updated_at, analysis_date=analysis_date, patient_id=patient_id)
        for i in tests:
            name = i['name']
            analysises = i['analysis']
            test = Test.objects.create(name=name, patient_test_id=patient_test)
            for j in analysises:
                value = j['value']
                indicator_name = j['indicator_name']
                try:
                    indicator = Indicator.objects.get(name=indicator_name)
                except Indicator.DoesNotExist:
                    raise NotFound('Indicator не существует')
                analysis = Analysis.objects.create(value=value, indicator_id=indicator, test_id=test)

        hematological_research_tests = Test.objects.filter(patient_test_id=patient_test,
                                                           name='hematological_research').first()
        immune_status_tests = Test.objects.filter(patient_test_id=patient_test,
                                                           name='immune_status').first()
        cytokine_status_tests = Test.objects.filter(patient_test_id=patient_test,
                                                           name='cytokine_status').first()
        if hematological_research_tests is not None:
            lymf_indicator = Indicator.objects.get(name='lymphocytes')
            mon_indicator = Indicator.objects.get(name='monocytes')
            neu_indicator = Indicator.objects.get(name='neutrophils')
            lymf = Analysis.objects.get(test_id=hematological_research_tests, indicator_id=lymf_indicator).value
            mon = Analysis.objects.get(test_id=hematological_research_tests, indicator_id=mon_indicator).value
            neu = Analysis.objects.get(test_id=hematological_research_tests, indicator_id=neu_indicator).value

            regeneration_type_min = [Decimal(3.4), Decimal(1.89), Decimal(6.4)]
            regeneration_type_max = [Decimal(6.1), Decimal(2.1), Decimal(12.8)]

            get_regeneration_type_result(hematological_research_tests,
                                         [lymf / mon, neu / lymf, neu / mon],
                                         regeneration_type_min,
                                         regeneration_type_max)

            draw_regeneration_type1([lymf / mon, neu / lymf, neu / mon], patient_test)

        if hematological_research_tests is not None and immune_status_tests is not None:
            lymf_indicator = Indicator.objects.get(name='lymphocytes')
            cd19_indicator = Indicator.objects.get(name='b_lymphocytes')
            neu_indicator = Indicator.objects.get(name='neutrophils')
            cd4_indicator = Indicator.objects.get(name='t_helpers')
            cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')
            cd3_indicator = Indicator.objects.get(name='t_lymphocytes')
            lymf = Analysis.objects.get(test_id=hematological_research_tests, indicator_id=lymf_indicator).value
            neu = Analysis.objects.get(test_id=hematological_research_tests, indicator_id=neu_indicator).value
            cd19 = Analysis.objects.get(test_id=immune_status_tests, indicator_id=cd19_indicator).value
            cd4 = Analysis.objects.get(test_id=immune_status_tests, indicator_id=cd4_indicator).value
            cd8 = Analysis.objects.get(test_id=immune_status_tests, indicator_id=cd8_indicator).value
            cd3 = Analysis.objects.get(test_id=immune_status_tests, indicator_id=cd3_indicator).value

            hematological_research_min, hematological_research_max = get_refs([(cd19_indicator, cd4_indicator, None),
                                                                     (lymf_indicator, cd19_indicator, None),
                                                                     (neu_indicator, lymf_indicator, None),
                                                                     (cd19_indicator, cd8_indicator, None)])
            # hematological_research_min = [cd19_indicator.interval_min /cd4_indicator.interval_min,
            #                               lymf_indicator.interval_min / cd19_indicator.interval_min,
            #                               neu_indicator.interval_min / lymf_indicator.interval_min,
            #                               cd19_indicator.interval_min / cd8_indicator.interval_min]
            #
            # hematological_research_max = [cd19_indicator.interval_max / cd4_indicator.interval_max,
            #                               lymf_indicator.interval_max / cd19_indicator.interval_max,
            #                               neu_indicator.interval_max / lymf_indicator.interval_max,
            #                               cd19_indicator.interval_max / cd8_indicator.interval_max]

            immune_status_min, immune_status_max = get_refs([(neu_indicator, cd4_indicator, None),
                                                                     (neu_indicator, cd3_indicator, None),
                                                                     (neu_indicator, lymf_indicator, None),
                                                                     (neu_indicator, cd8_indicator, None)])

            get_hematological_research_result(hematological_research_tests,
                                              [(cd19 / cd4), (lymf / cd19), (neu / lymf), (cd19 / cd8)],
                                              hematological_research_min, hematological_research_max)

            get_immune_status_result(immune_status_tests,
                                     [neu / cd4, neu / cd3, neu / lymf, neu / cd8],
                                     immune_status_min, immune_status_max)

            draw_hematological_research([(cd19 / cd4), (lymf / cd19), (neu / lymf), (cd19 / cd8)],
                                        patient_test)
            draw_immune_status([neu / cd4, neu / cd3, neu / lymf, neu / cd8], patient_test)

        if cytokine_status_tests is not None:
            cd3_il2_stimulated_indicator = Indicator.objects.get(name='cd3_il2_stimulated')
            cd3_il2_spontaneous_indicator = Indicator.objects.get(name='cd3_il2_spontaneous')

            cd3_tnfa_stimulated_indicator = Indicator.objects.get(name='cd3_tnfa_stimulated')
            cd3_tnfa_spontaneous_indicator = Indicator.objects.get(name='cd3_tnfa_spontaneous')

            cd3_ifny_stimulated_indicator = Indicator.objects.get(name='cd3_ifny_stimulated')
            cd3_ifny_spontaneous_indicator = Indicator.objects.get(name='cd3_ifny_spontaneous')

            cd3_il2_stimulated = Analysis.objects.get(test_id=cytokine_status_tests,
                                                      indicator_id=cd3_il2_stimulated_indicator).value
            cd3_il2_spontaneous = Analysis.objects.get(test_id=cytokine_status_tests,
                                                      indicator_id=cd3_il2_spontaneous_indicator).value
            cd3_tnfa_stimulated = Analysis.objects.get(test_id=cytokine_status_tests,
                                                      indicator_id=cd3_tnfa_stimulated_indicator).value
            cd3_tnfa_spontaneous = Analysis.objects.get(test_id=cytokine_status_tests,
                                                      indicator_id=cd3_tnfa_spontaneous_indicator).value
            cd3_ifny_stimulated = Analysis.objects.get(test_id=cytokine_status_tests,
                                                      indicator_id=cd3_ifny_stimulated_indicator).value
            cd3_ifny_spontaneous = Analysis.objects.get(test_id=cytokine_status_tests,
                                                       indicator_id=cd3_ifny_spontaneous_indicator).value

            cytokine_status_min = [80, 80, 80]
            cytokine_status_max = [120, 120, 120]

            get_cytokine_status_result(cytokine_status_tests,
                                       [cd3_il2_stimulated / cd3_il2_spontaneous,
                                        cd3_tnfa_stimulated / cd3_tnfa_spontaneous,
                                        cd3_ifny_stimulated / cd3_ifny_spontaneous],
                                       cytokine_status_min,
                                       cytokine_status_max)

            draw_cytokine_status([cd3_il2_stimulated / cd3_il2_spontaneous,
                                  cd3_tnfa_stimulated / cd3_tnfa_spontaneous,
                                  cd3_ifny_stimulated / cd3_ifny_spontaneous], patient_test)

        return Response(f'Анализ с id {patient_test.id} создан')


class PatientTestsEditView(APIView):
    """
    Эндпоинт для редактирования тестов пациента
    """
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['analysis_date', 'test'],
        properties={
            'analysis_date': openapi.Schema(type=openapi.TYPE_STRING),
            'test': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'analysis': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'value': openapi.Schema(type=openapi.TYPE_STRING),
                                    'indicator_name': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            )
        }
    ))
    def put(self, request, pk):
        analysis_date = request.data['analysis_date']
        doctor_id = request.user
        current_time = datetime.now()
        updated_at = current_time
        tests = request.data['test']
        try:
            patient_test = PatientTests.objects.get(id=pk, doctor_id=doctor_id)
        except PatientTests.DoesNotExist:
            raise NotFound('Patient Test не существует')
        PatientTests.objects.filter(id=pk, doctor_id=doctor_id).update(updated_at=updated_at,
                                                                       analysis_date=analysis_date)

        for i in tests:
            name = i['name']
            analyses = i['analysis']
            try:
                test = Test.objects.get(name=name, patient_test_id=patient_test)
            except Test.DoesNotExist:
                raise NotFound('Test не существует')
            for j in analyses:
                value = j['value']
                indicator_name = j['indicator_name']
                try:
                    indicator = Indicator.objects.get(name=indicator_name)
                except Indicator.DoesNotExist:
                    raise NotFound('Indicator не существует')
                Analysis.objects.filter(indicator_id=indicator, test_id=test).update(value=value)

        return Response('Анализ изменён')

names_dict = {
            'leukocytes': 'лейкоциты',
            'lymphocytes': 'лимфоциты',
            'monocytes': 'моноциты',
            'neutrophils': 'нейтрофилы',
            'eosinophils': 'эозинофилы',
            'basophils': 'базофилы',
            'hemoglobin': 'гемоглобин',
            'hematocrit': 'гематокрит',
            'platelets': 'тромбоциты',
            'erythrocytes': 'эритроциты',
            'avg_erythrocyte_volume': 'ср.объем эритроциты',
            'avg_hem_cont_in_eryth': 'ср.сод.гем. в эритроциты',
            'avg_hem_conc_in_eryth': 'ср.конц.гем в эритроциты',
            'eryth_volume_distr': 'распр.эритр. по объему',
            'ave_platelet_volume': 'ср.объем эритроцита',
            'thrombocrit': 'тромбокрит',
            'thromb_volume_distr': 'распр.тромб. по объему',
            'b_lymphocytes': 'б-лимфоциты',
            't_cytotoxic_lymphocytes': 'т-цитоксические лимфоциты',
            't_lymphocytes': 'т-лимфоциты',
            't_helpers': 'т-хелперы',
            'nk_cells': 'nk-клетки',
            'tnk': 'тнк',
            'active_t_lymphocytes': 'активные т-лимфоциты',
            'igA': 'igA',
            'igG': 'igG',
            'igM': 'igM',
            'circulating_immune_complexes': 'циркулирующие имунные комплексы',
            'nst_test_spontaneous': 'нст-тест (спонтанный)',
            'nst_test_stimulated': 'нст-тест (стимулированный)',
            'leukotytes_bactericidal_activity': 'бактерицидная активность лейкоцитов',
            'neutrophils_absorption_activity': 'поглотительная активность нейтрофилов',
            'monocytes_absorption_activity': 'поглотительная активность моноцитов',
            'cd3_ifny_stimulated': 'cd3+ifny+(стимулированный)',
            'cd3_ifny_spontaneous': 'cd3+ifny+(спонтанный)',
            'cd3_tnfa_stimulated': 'cd3+tnfa+(стимулированный)',
            'cd3_tnfa_spontaneous': 'cd3+tnfa+(спонтанный)',
            'cd3_il2_stimulated': 'cd3+il2+(стимулированный)',
            'cd3_il2_spontaneous': 'cd3+il2+(спонтанный)',
            'cd3_il4_stimulated': 'cd3+il4+(стимулированный)',
            'cd3_il4_spontaneous': 'cd3+il4+(спонтанный)',
            'cd3_negative_ifny_stimulated': 'cd3-ifny+(стимулированный)',
            'cd3_negative_ifny_spontaneous': 'cd3-ifny+(спонтанный)',
        }


class PatientAnalysisView(RetrieveAPIView):
    """
    Эндпоинт для вывода конкретного анализа(теста). В параметре пути передается id анализа(теста). Вывод в виде:
    {
    "name": "hematological_research",
    "analysis_date": "2024-03-24",
    "analysis": [
        {
            "name": "name",
            "value": 5.0,
            "interval_min": 4.5,
            "interval_max": 11.0,
            "unit": "10E9/л"
        }
    ]
    """
    serializer_class = TestNameSerializer
    queryset = Test.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        patient_test = PatientTests.objects.get(id=instance.patient_test_id.id)
        data['analysis_date'] = patient_test.analysis_date
        analysises = Analysis.objects.filter(test_id=instance)
        data['analysis'] = []
        for analysis in analysises:
            analysis_data = {
                'name': names_dict[analysis.indicator_id.name],
                'value': analysis.value,
                'interval_min': analysis.indicator_id.interval_min,
                'interval_max': analysis.indicator_id.interval_max,
                'unit': analysis.indicator_id.unit
            }
            data['analysis'].append(analysis_data)

        return Response(data)


class ConclusionView(RetrieveUpdateAPIView):
    """
    Эндпоинт для вывода/редактирования заключения и рекомендаций теста. В ссылке передается id теста
    """
    queryset = Test.objects.all()
    serializer_class = ConclusionSerializer


class ChangeRefsView(RetrieveUpdateAPIView):
    """
    Эндпоинт для изменения реф.значений. В ссылке передается id у Test.
    Для hematological_research:
    {
        "cd19_cd4_min": 1,
        "lymf_cd19_min": 1,
        "neu_lymf_min": 1,
        "cd19_cd8_min": 1,
        "cd19_cd4_max": 1,
        "lymf_cd19_max": 1,
        "neu_lymf_max": 1,
        "cd19_cd8_max": 1
    }
    Для immune_status:
    {
        "neu_cd4_min": 1,
        "neu_cd3_min": 1,
        "neu_lymf_min": 1,
        "neu_cd8_min": 1,
        "neu_cd4_max": 1,
        "neu_cd3_max": 1,
        "neu_lymf_max": 1,
        "neu_cd8_max": 1
    }
    Для cytokine_status:
    {
        "cd3_il2_min": 1,
        "cd3_tnfa_min": 1,
        "cd3_ifny_min": 1,
        "cd3_il2_max": 1,
        "cd3_tnfa_max": 1,
        "cd3_ifny_max": 1
    }
    Для regeneration_type:
    {
        "lymf_mon_min": 1,
        "neu_lymf_min": 1,
        "neu_mon_min": 1,
        "lymf_mon_max": 1,
        "neu_lymf_max": 1,
        "neu_mon_max": 1
    }
    """
    queryset = Test.objects.all()
    serializer_class = ChangeRefsSerializer

    def update(self, request,  *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        type_name = instance.name
        request_data = request.data

        if type_name == "hematological_research":
            change_hematological_refs(request_data, instance)
        if type_name == "immune_status":
            change_immune_refs(request_data, instance)
        if type_name == "cytokine_status":
            change_cytokine_refs(request_data, instance)
        if type_name == "regeneration_type":
            change_regeneration_refs(request_data, instance)

        return Response(type_name)


class AnalysisComparisonView(RetrieveAPIView):
    """
    Эндпоинт для вывода сравнений анализов (печатная форма), в ссылке передается id у Test
    Вывод в виде:{
    "analysis": [
        {
            "name": "cd3_il2_stimulated",
            "value": 140.0,
            "avg_prev_value": null,
            "interval_min": 0.33,
            "interval_max": 0.65,
            "unit": "10E9/л",
            "changes": null
        },
    ]
    """
    queryset = Test.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        patient_test = PatientTests.objects.get(id=instance.patient_test_id.id)
        patient_test_date = patient_test.analysis_date
        season = str(patient_test_date).split('-')[1]
        season_name = 'spring' if season in ['02', '03', '04', '05', '06', '07'] else 'autumn'

        if season_name == 'spring':
            patient_tests_prev = PatientTests.objects.filter(Q(patient_id_id=instance.patient_test_id.patient_id.id) &
                                                             Q(analysis_date__lt=instance.patient_test_id.analysis_date) &
                                                             Q(analysis_date__month__in=[2, 3, 4, 5, 6, 7])) \
                .values('id')
        else:
            patient_tests_prev = PatientTests.objects.filter(Q(patient_id_id=instance.patient_test_id.patient_id.id) &
                                                             Q(analysis_date__lt=instance.patient_test_id.analysis_date) &
                                                             Q(analysis_date__month__in=[8, 9, 10, 11, 12, 1])) \
                .values('id')

        tests_prev = Test.objects.filter(patient_test_id__in=patient_tests_prev) \
            .values('id')

        analysises_prev = Analysis.objects.filter(test_id__in=tests_prev)

        data['analysis'] = []

        tests = Test.objects.filter(patient_test_id=instance.patient_test_id).values('id')
        analysises = Analysis.objects.filter(test_id__in=tests).values('id', 'indicator_id__name',
                                                                       'value', 'indicator_id__unit',
                                                                       'indicator_id__interval_min',
                                                                       'indicator_id__interval_max')
        if analysises_prev:
            for analysis in analysises:
                name = analysis['indicator_id__name']
                avg = analysises_prev.filter(indicator_id__name=name).aggregate(Avg('value'))[
                    'value__avg']
                changes = (analysis['value'] - avg) / avg * 100
                res = {
                    'name': names_dict[name],
                    'value': analysis['value'],
                    'avg_prev_value': round(avg, 2),
                    'interval_min': analysis['indicator_id__interval_min'],
                    'interval_max': analysis['indicator_id__interval_max'],
                    'unit': analysis['indicator_id__unit'],
                    'changes': round(changes, 2)
                }
                data['analysis'].append(res)
        else:
            for analysis in analysises:
                name = analysis['indicator_id__name']
                avg = None
                changes = None
                res = {
                    'name': names_dict[name],
                    'value': analysis['value'],
                    'avg_prev_value': avg,
                    'interval_min': analysis['indicator_id__interval_min'],
                    'interval_max': analysis['indicator_id__interval_max'],
                    'unit': analysis['indicator_id__unit'],
                    'changes': changes
                }
                data['analysis'].append(res)

        return Response(data)



class SearchPatientView(GenericAPIView):
    serializer_class = SearchPatientSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        patronymic = data.get('patronymic', '')
        birth_date = data.get('birth_date', '')

        filters = Q()
        if first_name:
            filters &= Q(first_name__istartswith=first_name)
        if last_name:
            filters &= Q(last_name__istartswith=last_name)
        if patronymic:
            filters &= Q(patronymic__istartswith=patronymic)
        if birth_date:
            filters &= Q(birth_date=birth_date)

        patients = Patient.objects.filter(filters).values('id', 'first_name', 'last_name', 'patronymic', 'birth_date')

        data = [{'id': patient['id'],
                 'first_name': patient['first_name'],
                 'last_name': patient['last_name'],
                 'patronymic': patient['patronymic'],
                 'birth_date': patient['birth_date']} for patient in patients]

        return Response(data)


class GraphicCreateView(APIView):
    def post(self, request):
        data = request.data.get('values')
        draw_hematological_research(data)

        return Response('image created')


class GraphicView(RetrieveAPIView):
    """
    Эндпоинт для вывода ссылок графиков, в url передается id PatientTest
    """
    serializer_class = GraphicSerializer
    queryset = PatientTests.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        graphics = Graphic.objects.filter(patient_test_id=instance)
        serializer = self.get_serializer(graphics, many=True)
        data = serializer.data

        tests = Test.objects.filter(patient_test_id=instance).values("id")
        for i in data:
            i['graphic'] = i['graphic'][28:]
            i['test_name'] = '_'.join(i['graphic'].split('/')[2].split('.')[0].split('_')[:2])
            i['test_id'] = tests.filter(name=i['test_name'])
        # for i in data:
        #     i['graphic'] = i['graphic'][0:28] + i['graphic'][34:]

        return Response(data)
