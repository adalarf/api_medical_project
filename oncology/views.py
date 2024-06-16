from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView,\
    ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import DoctorSignupSerializer, BaseDoctorSerializer, DoctorLoginSerializer
from rest_framework.response import Response
from .models import Doctor, SubjectInfo, CopyrightInfo, Patient, Indicator, Test, PatientTests
from .serializers import SubjectInfoSerializer, CopyrightInfoSerializer, PatientSerializer, SubjectListSerializer,\
    IndicatorSerializer, GraphicSerializer, PatientInfoSerializer, TestNameSerializer, SearchPatientSerializer,\
    ConclusionSerializer, ChangeRefsSerializer, PatientOperationSerializer
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from oncology.services.test_service import get_tests_all_types, get_test_info_for_graphic
from oncology.services.patient_test_service import create_tests_and_analysises, update_tests_and_analysises,\
    draw_graphics_and_make_results, get_patient_tests_by_id
from oncology.services.doctor_service import set_doctor_password, get_doctor_by_email
from oncology.services.auth_service import create_token, get_or_create_token
from oncology.services.copyright_service import get_copyright_info
from oncology.services.patient_service import get_tests_for_patient, search_patients
from oncology.services.analysis_service import get_analysises_by_test_id, get_analysis_comparison,\
    get_analysises_and_analysis_prev_by_test_id
from oncology.services.result_service import save_conclusion_and_recommendations, change_refs
from oncology.services.graphic_service import get_graphics_by_patient_test_id


class DoctorSignupView(GenericAPIView):
    serializer_class = DoctorSignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = set_doctor_password(request)
            token = create_token(user)
            return Response({
                "token": token.key,
                "user": user.id,
            })
        return Response(serializer.errors)


class DoctorLoginView(GenericAPIView):
    serializer_class = DoctorLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            try:
                user = get_doctor_by_email(email)
            except Doctor.DoesNotExist:
                return Response({"error": "Неверный логин или пароль"})

            if not user.check_password(password):
                return Response({"error": "Неверный логин или пароль"})

            token, created = get_or_create_token(user)
            return Response({"token": token.key, "user": user.email})

        return Response(serializer.errors)


class LogoutView(APIView):

    def post(self, request, format=None):
        request.auth.delete()
        return Response("Вы вышли из аккаунта")


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
    permission_classes = [IsAuthenticated]

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

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        else:
            return [IsAuthenticated()]


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

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        else:
            return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = get_copyright_info(kwargs["pk"])
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
    permission_classes = [IsAuthenticated]


class IndicatorView(CreateAPIView):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticated]


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

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        patient = get_tests_for_patient(pk)

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
                if test.name != "regeneration_type":
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

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["analysis_date", "test", "patient_id"],
        properties={
            "analysis_date": openapi.Schema(type=openapi.TYPE_STRING),
            "test": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "analysis": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "value": openapi.Schema(type=openapi.TYPE_STRING),
                                    "indicator_name": openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            ),
            "patient_id": openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ))
    def post(self, request):
        analysis_date = request.data["analysis_date"]
        doctor_id = request.user
        current_time = datetime.now()
        created_at = current_time
        updated_at = current_time
        tests = request.data["test"]
        patient = request.data["patient_id"]

        patient_test = create_tests_and_analysises(patient, doctor_id, created_at, updated_at, analysis_date, tests)

        hematological_research_tests, immune_status_tests, cytokine_status_tests, regeneration_type_tests\
            = get_tests_all_types(patient_test)

        draw_graphics_and_make_results(patient_test, regeneration_type_tests, hematological_research_tests,
                                       immune_status_tests, cytokine_status_tests)

        return Response(f"Анализ с id {patient_test.id} создан")


class PatientTestsEditView(APIView):
    """
    Эндпоинт для редактирования тестов пациента
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["analysis_date", "test"],
        properties={
            "analysis_date": openapi.Schema(type=openapi.TYPE_STRING),
            "test": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "analysis": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "value": openapi.Schema(type=openapi.TYPE_STRING),
                                    "indicator_name": openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            )
        }
    ))
    def put(self, request, pk):
        analysis_date = request.data["analysis_date"]
        doctor_id = request.user
        current_time = datetime.now()
        updated_at = current_time
        tests = request.data["test"]

        update_tests_and_analysises(pk, doctor_id, updated_at, analysis_date, tests)

        return Response("Анализ изменён")


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
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        patient_test = get_patient_tests_by_id(instance.patient_test_id.id)
        data["analysis_date"] = patient_test.analysis_date
        analysises = get_analysises_by_test_id(instance)
        data["analysis"] = []
        for analysis in analysises:
            analysis_data = {
                "name": get_names_dict()[analysis.indicator_id.name],
                "value": analysis.value,
                "interval_min": analysis.indicator_id.interval_min,
                "interval_max": analysis.indicator_id.interval_max,
                "unit": analysis.indicator_id.unit
            }
            data["analysis"].append(analysis_data)

        return Response(data)


class ConclusionView(RetrieveUpdateAPIView):
    """
    Эндпоинт для вывода/редактирования заключения и рекомендаций теста. В ссылке передается id теста
    """
    queryset = Test.objects.all()
    serializer_class = ConclusionSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request,  *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        type_name = instance.name
        request_data = request.data
        serializer_data = serializer.data
        save_conclusion_and_recommendations(instance, type_name, request_data)
        return Response(serializer_data)


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
    permission_classes = [IsAuthenticated]

    def update(self, request,  *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        type_name = instance.name
        request_data = request.data

        change_refs(instance, type_name, request_data)

        return Response("Реф. значения изменены")


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
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        patient_test = get_patient_tests_by_id(instance.patient_test_id.id)
        patient_test_date = patient_test.analysis_date
        analysises_prev, analysises = get_analysises_and_analysis_prev_by_test_id(instance, patient_test_date)
        data["analysis"] = []

        data = get_analysis_comparison(data, analysises_prev, analysises, get_names_dict())
        return Response(data)


class OperationInfoView(RetrieveUpdateAPIView):
    """
    Эндпоинт для вывода/редактирования информации с операцией. В заголовке передается id пациента
    """
    queryset = Patient.objects.all()
    serializer_class = PatientOperationSerializer
    permission_classes = [IsAuthenticated]


class SearchPatientView(GenericAPIView):
    serializer_class = SearchPatientSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        patronymic = data.get("patronymic", "")
        birth_date = data.get("birth_date", "")

        patients = search_patients(first_name, last_name, patronymic, birth_date)
        if not patients:
            return Response([{"error": "Пациент с такими данными не найден"}])

        data = [{"id": patient["id"],
                 "first_name": patient["first_name"],
                 "last_name": patient["last_name"],
                 "patronymic": patient["patronymic"],
                 "birth_date": patient["birth_date"]} for patient in patients]

        return Response(data)


class GraphicView(RetrieveAPIView):
    """
    Эндпоинт для вывода ссылок графиков, в url передается id PatientTest
    """
    serializer_class = GraphicSerializer
    queryset = PatientTests.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        graphics = get_graphics_by_patient_test_id(instance)
        serializer = self.get_serializer(graphics, many=True)
        data = serializer.data

        data = get_test_info_for_graphic(instance, data)

        return Response(data)


def get_names_dict():
    names_dict = {
        "leukocytes": "лейкоциты",
        "lymphocytes": "лимфоциты",
        "monocytes": "моноциты",
        "neutrophils": "нейтрофилы",
        "eosinophils": "эозинофилы",
        "basophils": "базофилы",
        "hemoglobin": "гемоглобин",
        "hematocrit": "гематокрит",
        "platelets": "тромбоциты",
        "erythrocytes": "эритроциты",
        "avg_erythrocyte_volume": "ср.объем эритроциты",
        "avg_hem_cont_in_eryth": "ср.сод.гем. в эритроциты",
        "avg_hem_conc_in_eryth": "ср.конц.гем в эритроциты",
        "eryth_volume_distr": "распр.эритр. по объему",
        "ave_platelet_volume": "ср.объем эритроцита",
        "thrombocrit": "тромбокрит",
        "thromb_volume_distr": "распр.тромб. по объему",
        "b_lymphocytes": "б-лимфоциты",
        "t_cytotoxic_lymphocytes": "т-цитоксические лимфоциты",
        "t_lymphocytes": "т-лимфоциты",
        "t_helpers": "т-хелперы",
        "nk_cells": "nk-клетки",
        "tnk": "тнк",
        "active_t_lymphocytes": "активные т-лимфоциты",
        "igA": "igA",
        "igG": "igG",
        "igM": "igM",
        "circulating_immune_complexes": "циркулирующие имунные комплексы",
        "nst_test_spontaneous": "нст-тест (спонтанный)",
        "nst_test_stimulated": "нст-тест (стимулированный)",
        "leukotytes_bactericidal_activity": "бактерицидная активность лейкоцитов",
        "neutrophils_absorption_activity": "поглотительная активность нейтрофилов",
        "monocytes_absorption_activity": "поглотительная активность моноцитов",
        "cd3_ifny_stimulated": "cd3+ifny+(стимулированный)",
        "cd3_ifny_spontaneous": "cd3+ifny+(спонтанный)",
        "cd3_tnfa_stimulated": "cd3+tnfa+(стимулированный)",
        "cd3_tnfa_spontaneous": "cd3+tnfa+(спонтанный)",
        "cd3_il2_stimulated": "cd3+il2+(стимулированный)",
        "cd3_il2_spontaneous": "cd3+il2+(спонтанный)",
        "cd3_il4_stimulated": "cd3+il4+(стимулированный)",
        "cd3_il4_spontaneous": "cd3+il4+(спонтанный)",
        "cd3_negative_ifny_stimulated": "cd3-ifny+(стимулированный)",
        "cd3_negative_ifny_spontaneous": "cd3-ifny+(спонтанный)",
    }
    return names_dict
