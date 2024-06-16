from oncology.models import Test, Patient, PatientTests, Analysis
from rest_framework.exceptions import NotFound
from oncology.services.graphic_service import draw_hematological_research, draw_immune_status, draw_cytokine_status,\
    draw_regeneration_type1
from oncology.services.result_service import get_regeneration_analysis_and_make_result,\
    get_hematological_and_immune_analysis_and_make_result, get_cytokine_analysis_and_make_result
from oncology.services.indicator_service import get_value_and_indicator
from oncology.services.test_service import change_hematological_and_immune_values, change_regeneration_values,\
    change_cytokine_values
from django.db.models import Q


def create_patient_tests(patient, doctor_id, created_at, updated_at, analysis_date):
    try:
        patient_id = Patient.objects.get(id=patient)
    except Patient.DoesNotExist:
        raise NotFound('Пациент не найден')
    patient_test = PatientTests.objects.create(doctor_id=doctor_id, created_at=created_at, updated_at=updated_at,
                                               analysis_date=analysis_date, patient_id=patient_id)
    return patient_test


def update_patient_tests(patient, doctor_id, updated_at, analysis_date):
    try:
        patient_test = PatientTests.objects.get(id=patient, doctor_id=doctor_id)
    except PatientTests.DoesNotExist:
        raise NotFound('Patient Test не существует')
    PatientTests.objects.filter(id=patient, doctor_id=doctor_id).update(updated_at=updated_at,
                                                                        analysis_date=analysis_date)
    return patient_test


def create_tests_and_analysises(patient, doctor_id, created_at, updated_at, analysis_date, tests):
    patient_test = create_patient_tests(patient, doctor_id, created_at, updated_at, analysis_date)

    for i in tests:
        name = i['name']
        analysises = i['analysis']
        test = Test.objects.create(name=name, patient_test_id=patient_test)
        if name == 'hematological_research':
            regeneration_type_test = Test.objects.create(name='regeneration_type', patient_test_id=patient_test)
        for j in analysises:
            value, indicator = get_value_and_indicator(j)
            Analysis.objects.create(value=value, indicator_id=indicator, test_id=test)
            if name == 'hematological_research':
                Analysis.objects.create(value=value, indicator_id=indicator,
                                        test_id=regeneration_type_test)

    return patient_test


def update_tests_and_analysises(patient, doctor_id, updated_at, analysis_date, tests):
    patient_test = update_patient_tests(patient, doctor_id, updated_at, analysis_date)

    for i in tests:
        name = i['name']
        analyses = i['analysis']
        try:
            test = Test.objects.get(name=name, patient_test_id=patient_test)
        except Test.DoesNotExist:
            raise NotFound('Test не существует')
        for j in analyses:
            value, indicator = get_value_and_indicator(j)
            Analysis.objects.filter(indicator_id=indicator, test_id=test).update(value=value)

            if name == "hematological_research":
                change_regeneration_values(test, patient_test)
                change_hematological_and_immune_values(test, patient_test, 'hematological_research', 'immune_status')

            if name == "immune_status":
                change_hematological_and_immune_values(test, patient_test, 'immune_status', 'hematological_research')

            if name == 'cytokine_status':
                change_cytokine_values(test, patient_test)


def draw_graphics_and_make_results(patient_test, regeneration_type_tests, hematological_research_tests,
                                   immune_status_tests, cytokine_status_tests):
    if regeneration_type_tests is not None:
        regeneration_analysis = get_regeneration_analysis_and_make_result(regeneration_type_tests)

        draw_regeneration_type1(regeneration_analysis, patient_test)

    if hematological_research_tests is not None and immune_status_tests is not None:
        hematological_and_immune_analysis = get_hematological_and_immune_analysis_and_make_result(
            hematological_research_tests, immune_status_tests)

        draw_hematological_research(hematological_and_immune_analysis["hematological_analysis"],
                                    patient_test)
        draw_immune_status(hematological_and_immune_analysis["immune_analysis"], patient_test)

    if cytokine_status_tests is not None:
        cytokine_analysis = get_cytokine_analysis_and_make_result(cytokine_status_tests)

        draw_cytokine_status(cytokine_analysis, patient_test)


def get_patient_tests_by_id(patient_tests_id):
    return PatientTests.objects.get(id=patient_tests_id)


def get_patient_tests_by_patient_id_and_analysis_date(instance, months):
    return PatientTests.objects.filter(Q(patient_id_id=instance.patient_test_id.patient_id.id) &
                                       Q(analysis_date__lt=instance.patient_test_id.analysis_date) &
                                       Q(analysis_date__month__in=months)).values('id')
