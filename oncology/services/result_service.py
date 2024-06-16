from decimal import Decimal
from oncology.models import Test
from oncology.services.analysis_service import get_hematological_and_immune_analysis, get_regeneration_analysis, \
    get_cytokine_analysis
from oncology.services.indicator_service import get_regeneration_indicators, get_hematological_and_immune_indicators, \
    get_hematological_refs, get_immune_refs, get_cytokine_indicators
from oncology.services.test_service import change_hematological_refs, change_regeneration_refs,\
    change_immune_refs, change_cytokine_refs, get_tests_by_patient_id_and_name


def get_analysis_result(tests: Test, values, min_values, max_values):
    for i in range(len(values)):
        if not (min_values[i] <= values[i] <= max_values[i]):
            tests.conclusion = "значения с отклонениями от нормы"
            tests.recommendations = "test"
            tests.save()
            return
    tests.conclusion = "значения в пределах нормы"
    tests.recommendations = "test"
    tests.save()


def save_conclusion_and_recommendations(instance, type_name, request_data):
    tests = get_tests_by_patient_id_and_name(instance, type_name)
    for test in tests:
        test.recommendations = request_data['recommendations']
        test.conclusion = request_data['conclusion']
        test.save()


def change_refs(instance, type_name, request_data):
    tests = get_tests_by_patient_id_and_name(instance, type_name)
    if type_name == "hematological_research":
        for test in tests:
            change_hematological_refs(request_data, test)
    if type_name == "immune_status":
        for test in tests:
            change_immune_refs(request_data, test)
    if type_name == "cytokine_status":
        for test in tests:
            change_cytokine_refs(request_data, test)
    if type_name == "regeneration_type":
        for test in tests:
            change_regeneration_refs(request_data, test)


def get_hematological_and_immune_analysis_and_make_result(hematological_research_tests, immune_status_tests):
    hematological_and_immune_indicators = get_hematological_and_immune_indicators()
    hematological_and_immune_analysis = get_hematological_and_immune_analysis(
        hematological_research_tests, immune_status_tests, hematological_and_immune_indicators)

    hematological_research_min, hematological_research_max = get_hematological_refs(
        hematological_and_immune_indicators, [None, None, None, None])

    immune_status_min, immune_status_max = get_immune_refs(hematological_and_immune_indicators,
                                                           [None, None, None, None])

    get_analysis_result(hematological_research_tests,
                        hematological_and_immune_analysis["hematological_analysis"],
                        hematological_research_min, hematological_research_max)

    get_analysis_result(immune_status_tests,
                        hematological_and_immune_analysis["immune_analysis"],
                        immune_status_min, immune_status_max)

    return hematological_and_immune_analysis


def get_regeneration_analysis_and_make_result(regeneration_type_tests):
    regeneration_indicators = get_regeneration_indicators()

    regeneration_analysis = get_regeneration_analysis(regeneration_type_tests, regeneration_indicators)

    regeneration_type_min = [Decimal(3.4), Decimal(1.89), Decimal(6.4)]
    regeneration_type_max = [Decimal(6.1), Decimal(2.1), Decimal(12.8)]

    get_analysis_result(regeneration_type_tests, regeneration_analysis,
                        regeneration_type_min, regeneration_type_max)

    return regeneration_analysis


def get_cytokine_analysis_and_make_result(cytokine_status_tests):
    cytokine_indicators = get_cytokine_indicators()

    cytokine_analysis = get_cytokine_analysis(cytokine_status_tests, cytokine_indicators)

    cytokine_status_min = [80, 80, 80]
    cytokine_status_max = [120, 120, 120]

    get_analysis_result(cytokine_status_tests, cytokine_analysis, cytokine_status_min, cytokine_status_max)

    return cytokine_analysis
