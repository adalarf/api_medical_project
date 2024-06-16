from oncology.models import Patient, PatientTests
from django.db.models import Prefetch, Q


def get_tests_for_patient(pk):
    return Patient.objects.prefetch_related(
        Prefetch('patienttests_set', queryset=PatientTests.objects.prefetch_related('test_set'))
    ).get(pk=pk)


def search_patients(first_name, last_name, patronymic, birth_date):
    filters = Q()
    if first_name:
        filters &= Q(first_name__istartswith=first_name)
    if last_name:
        filters &= Q(last_name__istartswith=last_name)
    if patronymic:
        filters &= Q(patronymic__istartswith=patronymic)
    if birth_date:
        filters &= Q(birth_date=birth_date)

    return Patient.objects.filter(filters).values('id', 'first_name', 'last_name', 'patronymic', 'birth_date')
