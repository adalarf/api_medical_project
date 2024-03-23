from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import DoctorSignupSerializer, BaseDoctorSerializer, DoctorLoginSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Doctor, SubjectInfo, CopyrightInfo
from .serializers import SubjectInfoSerializer, CopyrightInfoSerializer


class DoctorSignupView(GenericAPIView):
    serializer_class = DoctorSignupSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = Doctor.objects.get(login=request.data['login'])
            user.set_password(request.data['password'])
            user.is_active = True
            user.save()
            token = Token.objects.create(user=user)
            return Response({
                'token': token.key,
                'user': user.id,
            })
        return Response({})


class DoctorLoginView(GenericAPIView):
    serializer_class = DoctorLoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            login = serializer.validated_data.get('login')
            password = serializer.validated_data.get('password')

            try:
                user = Doctor.objects.get(login=login)
            except Doctor.DoesNotExist:
                return Response({'error': 'Неверный логин или пароль'})

            if not user.check_password(password):
                return Response({'error': 'Неверный логин или пароль'})

            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': user.login})

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
    lookup_field = 'subject_name'


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