from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomManager(BaseUserManager):
    def create_user(self, first_name,  last_name, patronymic, password, email, **extra_fields):
        doctor = self.model(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            email=self.normalize_email(email),
            **extra_fields
        )
        doctor.set_password(password)
        doctor.save(using=self._db)
        return doctor

    def create_superuser(self, first_name,  last_name, patronymic, password, email, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff = True")

        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser = True")
        return self.create_user(first_name,  last_name, patronymic, password, email, **extra_fields)


class Doctor(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "patronymic"]

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True


def validate_date(value):
    if value > timezone.now().date():
        raise ValidationError("Дата рождения не может быть больше текущей даты")


class Patient(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    birth_date = models.DateField(validators=[validate_date])
    diagnosis = models.CharField(max_length=255)
    diagnosis_date = models.DateField(null=True, blank=True)
    chemoterapy = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255)
    diagnosis_comment = models.TextField(null=True, blank=True)
    operation_comment = models.TextField(null=True, blank=True)
    chemoterapy_comment = models.TextField(null=True, blank=True)


class PatientTests(models.Model):
    analysis_date = models.DateField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    doctor_id = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    patient_id = models.ForeignKey(Patient, on_delete=models.PROTECT)


class Test(models.Model):
    name = models.CharField(max_length=255)
    conclusion = models.TextField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    patient_test_id = models.ForeignKey("PatientTests", on_delete=models.PROTECT)


class Analysis(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    indicator_id = models.ForeignKey("Indicator", on_delete=models.PROTECT)
    test_id = models.ForeignKey("Test", on_delete=models.PROTECT)


class Indicator(models.Model):
    name = models.CharField(max_length=255)
    interval_min = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    interval_max = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)


class SubjectInfo(models.Model):
    subject_name = models.CharField(max_length=255, unique=True)
    subject_text = models.TextField()


class CopyrightInfo(models.Model):
    copyright_text = models.TextField()


class Graphic(models.Model):
    graphic = models.ImageField(upload_to="media")
    patient_test_id = models.ForeignKey("PatientTests", on_delete=models.PROTECT)
