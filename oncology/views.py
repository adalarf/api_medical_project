from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import DoctorSignupSerializer, BaseDoctorSerializer, DoctorLoginSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Doctor, SubjectInfo, CopyrightInfo, Patient, Indicator, Test, Analysis, PatientTests
from .serializers import SubjectInfoSerializer, CopyrightInfoSerializer, PatientSerializer, SubjectListSerializer, PatientTestsSerializer, IndicatorSerializer, TestSerializer
from datetime import datetime
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


class IndicatorView(CreateAPIView):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer


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



        return Response('анализ создан')


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

        return Response('анализ изменён')
