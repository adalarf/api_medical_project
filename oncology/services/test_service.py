from oncology.models import Test, Analysis, Patient, PatientTests
from .analysis_service import get_cytokine_analysis
from .graphic_service import recreate_regeneration_or_cytokine_graphic, recreate_hematological_and_immune_graphic
from .indicator_service import get_hematological_indicators, get_immune_indicators, get_hematological_refs, \
    get_immune_refs, get_cytokine_indicators
from .result_service import get_analysis_result, get_regeneration_analysis_and_make_result, \
    get_hematological_and_immune_analysis_and_make_result
from decimal import Decimal


def change_hematological_refs(request_data, instance):
    hematological_indicators = get_hematological_indicators()

    hematological_research_min, hematological_research_max = get_hematological_refs(hematological_indicators,
                                                                                    [None, None, None, None])

    cd19_cd4_min = request_data.get("cd19_cd4_min", hematological_research_min[0])
    lymf_cd19_min = request_data.get("lymf_cd19_min", hematological_research_min[1])
    neu_lymf_min = request_data.get("neu_lymf_min", hematological_research_min[2])
    cd19_cd8_min = request_data.get("cd19_cd8_min", hematological_research_min[3])

    cd19_cd4_max = request_data.get("cd19_cd4_max", hematological_research_max[0])
    lymf_cd19_max = request_data.get("lymf_cd19_max", hematological_research_max[1])
    neu_lymf_max = request_data.get("neu_lymf_max", hematological_research_max[2])
    cd19_cd8_max = request_data.get("cd19_cd8_max", hematological_research_max[3])

    min_values = [cd19_cd4_min, lymf_cd19_min, neu_lymf_min, cd19_cd8_min]
    max_values = [cd19_cd4_max, lymf_cd19_max, neu_lymf_max, cd19_cd8_max]

    hematological_test = Test.objects.get(patient_test_id=instance.patient_test_id,
                                          name="hematological_research")
    immune_test = Test.objects.get(patient_test_id=instance.patient_test_id,
                                   name="immune_status")

    hematological_analysis = Analysis.objects.filter(test_id=hematological_test)
    immune_analysis = Analysis.objects.filter(test_id=immune_test)

    cd19 = immune_analysis.get(indicator_id__name='b_lymphocytes').value
    cd4 = immune_analysis.get(indicator_id__name='t_helpers').value
    lymf = hematological_analysis.get(indicator_id__name='lymphocytes').value
    neu = hematological_analysis.get(indicator_id__name='neutrophils').value
    cd8 = immune_analysis.get(indicator_id__name='t_cytotoxic_lymphocytes').value

    values = [cd19 / cd4, lymf / cd19, neu / lymf, cd19 / cd8]

    get_analysis_result(instance, values, min_values, max_values)


def change_immune_refs(request_data, instance):
    immune_indicators = get_immune_indicators()

    immune_status_min, immune_status_max = get_immune_refs(immune_indicators, [None, None, None, None])

    neu_cd4_min = request_data.get("neu_cd4_min", immune_status_min[0])
    neu_cd3_min = request_data.get("neu_cd3_min", immune_status_min[1])
    neu_lymf_min = request_data.get("neu_lymf_min", immune_status_min[2])
    neu_cd8_min = request_data.get("neu_cd8_min", immune_status_min[3])

    neu_cd4_max = request_data.get("neu_cd4_max", immune_status_max[0])
    neu_cd3_max = request_data.get("neu_cd3_max", immune_status_max[1])
    neu_lymf_max = request_data.get("neu_lymf_max", immune_status_max[2])
    neu_cd8_max = request_data.get("neu_cd8_max", immune_status_max[3])

    min_values = [neu_cd4_min, neu_cd3_min, neu_lymf_min, neu_cd8_min]
    max_values = [neu_cd4_max, neu_cd3_max, neu_lymf_max, neu_cd8_max]

    hematological_test = Test.objects.get(patient_test_id=instance.patient_test_id,
                                          name="hematological_research")
    immune_test = Test.objects.get(patient_test_id=instance.patient_test_id,
                                   name="immune_status")

    hematological_analysis = Analysis.objects.filter(test_id=hematological_test)
    immune_analysis = Analysis.objects.filter(test_id=immune_test)

    neu = hematological_analysis.get(indicator_id__name='neutrophils').value
    cd4 = immune_analysis.get(indicator_id__name='t_helpers').value
    cd3 = immune_analysis.get(indicator_id__name='t_lymphocytes').value
    lymf = hematological_analysis.get(indicator_id__name='lymphocytes').value
    cd8 = immune_analysis.get(indicator_id__name='t_cytotoxic_lymphocytes').value

    values = [neu / cd4, neu / cd3, neu / lymf, neu / cd8]

    get_analysis_result(instance, values, min_values, max_values)


def change_cytokine_refs(request_data, instance):
    cytokine_status_min = [80, 80, 80]
    cytokine_status_max = [120, 120, 120]

    cd3_il2_min = request_data.get("cd3_il2_min", cytokine_status_min[0])
    cd3_tnfa_min = request_data.get("cd3_tnfa_min", cytokine_status_min[1])
    cd3_ifny_min = request_data.get("cd3_ifny_min", cytokine_status_min[2])

    cd3_il2_max = request_data.get("cd3_il2_max", cytokine_status_max[0])
    cd3_tnfa_max = request_data.get("cd3_tnfa_max", cytokine_status_max[1])
    cd3_ifny_max = request_data.get("cd3_ifny_max", cytokine_status_max[2])

    min_values = [cd3_il2_min, cd3_tnfa_min, cd3_ifny_min]
    max_values = [cd3_il2_max, cd3_tnfa_max, cd3_ifny_max]

    cytokine_test = Test.objects.get(patient_test_id=instance.patient_test_id,
                                     name="cytokine_status")

    cytokine_analysis = Analysis.objects.filter(test_id=cytokine_test)

    cd3_il2_stimulated = cytokine_analysis.get(indicator_id__name='cd3_il2_stimulated').value
    cd3_il2_spontaneous = cytokine_analysis.get(indicator_id__name='cd3_il2_spontaneous').value
    cd3_tnfa_stimulated = cytokine_analysis.get(indicator_id__name='cd3_tnfa_stimulated').value
    cd3_tnfa_spontaneous = cytokine_analysis.get(indicator_id__name='cd3_tnfa_spontaneous').value
    cd3_ifny_stimulated = cytokine_analysis.get(indicator_id__name='cd3_ifny_stimulated').value
    cd3_ifny_spontaneous = cytokine_analysis.get(indicator_id__name='cd3_ifny_spontaneous').value

    values = [cd3_il2_stimulated / cd3_il2_spontaneous,
              cd3_tnfa_stimulated / cd3_tnfa_spontaneous,
              cd3_ifny_stimulated / cd3_ifny_spontaneous]

    get_analysis_result(instance, values, min_values, max_values)


def change_regeneration_refs(request_data, instance):
    regeneration_type_min = [Decimal(3.4), Decimal(1.89), Decimal(6.4)]
    regeneration_type_max = [Decimal(6.1), Decimal(2.1), Decimal(12.8)]

    lymf_mon_min = request_data.get("lymf_mon_min", regeneration_type_min[0])
    neu_lymf_min = request_data.get("neu_lymf_min", regeneration_type_min[1])
    neu_mon_min = request_data.get("neu_mon_min", regeneration_type_min[2])

    lymf_mon_max = request_data.get("lymf_mon_max", regeneration_type_max[0])
    neu_lymf_max = request_data.get("neu_lymf_max", regeneration_type_max[1])
    neu_mon_max = request_data.get("neu_mon_max", regeneration_type_max[2])

    min_values = [lymf_mon_min, neu_lymf_min, neu_mon_min]
    max_values = [lymf_mon_max, neu_lymf_max, neu_mon_max]

    regeneration_test = Test.objects.get(patient_test_id=instance.patient_test_id,
                                         name="regeneration_type")
    regeneration_analysis = Analysis.objects.filter(test_id=regeneration_test)

    lymf = regeneration_analysis.get(indicator_id__name='lymphocytes').value
    mon = regeneration_analysis.get(indicator_id__name='monocytes').value
    neu = regeneration_analysis.get(indicator_id__name='neutrophils').value

    values = [lymf / mon, neu / lymf, neu / mon]

    get_analysis_result(instance, values, min_values, max_values)


def get_tests_all_types(patient_test):
    hematological_research_tests = Test.objects.filter(patient_test_id=patient_test,
                                                       name='hematological_research').first()
    immune_status_tests = Test.objects.filter(patient_test_id=patient_test,
                                              name='immune_status').first()
    cytokine_status_tests = Test.objects.filter(patient_test_id=patient_test,
                                                name='cytokine_status').first()
    regeneration_type_tests = Test.objects.filter(patient_test_id=patient_test,
                                                  name='regeneration_type').first()

    return hematological_research_tests, immune_status_tests, cytokine_status_tests, regeneration_type_tests


def get_test_info_for_graphic(instance, data):
    tests = Test.objects.filter(patient_test_id=instance).values("id", "conclusion", "recommendations")
    for i in data:
        i['graphic'] = i['graphic'][28:]
        i['test_name'] = '_'.join(i['graphic'].split('/')[2].split('.')[0].split('_')[:2])
        test = tests.filter(name=i['test_name']).first()
        if test:
            i['test_id'] = test['id']
            i["conclusion"] = test['conclusion']
            i['recommendations'] = test['recommendations']
        else:
            i['test_id'] = None
            i["conclusion"] = None
            i['recommendations'] = None

    return data


def get_tests_by_patient_id_and_name(instance, type_name):
    instance_patient = Patient.objects.get(id=instance.patient_test_id.patient_id.id)
    patients = Patient.objects.filter(diagnosis=instance_patient.diagnosis).values_list("id", flat=True)
    if type_name == 'hematological_research' or type_name == 'immune_status':
        patient_tests = PatientTests.objects.filter(patient_id__id__in=patients, test__name="hematological_research"
                                                    ).filter(test__name="immune_status").values_list("id",
                                                                                                     flat=True)
        tests = Test.objects.filter(patient_test_id__patient_id__id__in=patient_tests, name=type_name)
    else:
        tests = Test.objects.filter(patient_test_id__patient_id__id__in=patients, name=type_name)

    return tests


def change_regeneration_values(test, patient_test):
    regeneration_type_test = Test.objects.filter(name='regeneration_type', patient_test_id=patient_test).first()
    if not regeneration_type_test:
        regeneration_type_test = test

    regeneration_analysis = get_regeneration_analysis_and_make_result(regeneration_type_test)

    recreate_regeneration_or_cytokine_graphic(test, 'regeneration_type',
                                              regeneration_analysis, patient_test)


def change_hematological_and_immune_values(test, patient_test, type_test, other_type_test):
    other_type_tests = Test.objects.filter(name=other_type_test, patient_test_id=patient_test).first()
    if other_type_tests:
        if type_test == 'hematological_research':
            hematological_and_immune_analysis = get_hematological_and_immune_analysis_and_make_result(
                test, other_type_test)
        else:
            hematological_and_immune_analysis = get_hematological_and_immune_analysis_and_make_result(
                other_type_test, test)

        recreate_hematological_and_immune_graphic(test, type_test,
                                                  hematological_and_immune_analysis, patient_test)


def change_cytokine_values(test, patient_test):
    cytokine_indicators = get_cytokine_indicators()

    cytokine_analysis = get_cytokine_analysis(test, cytokine_indicators)

    cytokine_status_min = [80, 80, 80]
    cytokine_status_max = [120, 120, 120]

    get_analysis_result(test, cytokine_analysis, cytokine_status_min, cytokine_status_max)

    recreate_regeneration_or_cytokine_graphic(test, 'cytokine_status', cytokine_analysis, patient_test)
