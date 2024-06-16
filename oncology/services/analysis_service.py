from django.db.models import Avg
from oncology.models import Analysis, Test
from oncology.services.patient_test_service import get_patient_tests_by_patient_id_and_analysis_date


def get_regeneration_analysis(regeneration_type_tests, regeneration_indicators):
    lymf = Analysis.objects.get(test_id=regeneration_type_tests,
                                indicator_id=regeneration_indicators["lymf_indicator"]).value
    mon = Analysis.objects.get(test_id=regeneration_type_tests,
                               indicator_id=regeneration_indicators["mon_indicator"]).value
    neu = Analysis.objects.get(test_id=regeneration_type_tests,
                               indicator_id=regeneration_indicators["neu_indicator"]).value

    regeneration_analysis = [lymf / mon, neu / lymf, neu / mon]

    return regeneration_analysis


def get_hematological_and_immune_analysis(hematological_research_tests, immune_status_tests,
                                          hematological_and_immune_indicators):
    lymf = Analysis.objects.get(test_id=hematological_research_tests,
                                indicator_id=hematological_and_immune_indicators["lymf_indicator"]).value
    neu = Analysis.objects.get(test_id=hematological_research_tests,
                               indicator_id=hematological_and_immune_indicators["neu_indicator"]).value
    cd19 = Analysis.objects.get(test_id=immune_status_tests,
                                indicator_id=hematological_and_immune_indicators["cd19_indicator"]).value
    cd4 = Analysis.objects.get(test_id=immune_status_tests,
                               indicator_id=hematological_and_immune_indicators["cd4_indicator"]).value
    cd8 = Analysis.objects.get(test_id=immune_status_tests,
                               indicator_id=hematological_and_immune_indicators["cd8_indicator"]).value
    cd3 = Analysis.objects.get(test_id=immune_status_tests,
                               indicator_id=hematological_and_immune_indicators["cd3_indicator"]).value

    hematological_analysis = [cd19 / cd4, lymf / cd19, neu / lymf, cd19 / cd8]
    immune_analysis = [neu / cd4, neu / cd3, neu / lymf, neu / cd8]

    hematological_and_immune_analysis = {
        "hematological_analysis": hematological_analysis,
        "immune_analysis": immune_analysis,
    }

    return hematological_and_immune_analysis


def get_cytokine_analysis(cytokine_status_tests, cytokine_indicators):
    cd3_il2_stimulated = Analysis.objects.get(test_id=cytokine_status_tests,
                                              indicator_id=cytokine_indicators["cd3_il2_stimulated_indicator"]).value
    cd3_il2_spontaneous = Analysis.objects.get(test_id=cytokine_status_tests,
                                               indicator_id=cytokine_indicators["cd3_il2_spontaneous_indicator"]).value
    cd3_tnfa_stimulated = Analysis.objects.get(test_id=cytokine_status_tests,
                                               indicator_id=cytokine_indicators["cd3_tnfa_stimulated_indicator"]).value
    cd3_tnfa_spontaneous = Analysis.objects.get(test_id=cytokine_status_tests,
                                                indicator_id=cytokine_indicators[
                                                    "cd3_tnfa_spontaneous_indicator"]).value
    cd3_ifny_stimulated = Analysis.objects.get(test_id=cytokine_status_tests,
                                               indicator_id=cytokine_indicators["cd3_ifny_stimulated_indicator"]).value
    cd3_ifny_spontaneous = Analysis.objects.get(test_id=cytokine_status_tests,
                                                indicator_id=cytokine_indicators[
                                                    "cd3_ifny_spontaneous_indicator"]).value

    cytokine_analysis = [
        cd3_il2_stimulated / cd3_il2_spontaneous,
        cd3_tnfa_stimulated / cd3_tnfa_spontaneous,
        cd3_ifny_stimulated / cd3_ifny_spontaneous
    ]

    return cytokine_analysis


def get_analysises_by_test_id(test_id):
    return Analysis.objects.filter(test_id=test_id)


def get_analysises_and_analysis_prev_by_test_id(instance, patient_test_date):
    season = str(patient_test_date).split("-")[1]
    if season in ["02", "03", "04", "05", "06", "07"]:
        patient_tests_prev = get_patient_tests_by_patient_id_and_analysis_date(instance, [2, 3, 4, 5, 6, 7])
    else:
        patient_tests_prev = get_patient_tests_by_patient_id_and_analysis_date(instance, [8, 9, 10, 11, 12, 1])

    tests_prev = Test.objects.filter(patient_test_id__in=patient_tests_prev).exclude(name="regeneration_type") \
        .values("id")

    analysises_prev = Analysis.objects.filter(test_id__in=tests_prev)

    tests = Test.objects.filter(patient_test_id=instance.patient_test_id).values("id").exclude(name="regeneration_type")
    analysises = Analysis.objects.filter(test_id__in=tests).values("id", "indicator_id__name",
                                                                   "value", "indicator_id__unit",
                                                                   "indicator_id__interval_min",
                                                                   "indicator_id__interval_max")
    return analysises_prev, analysises


def get_analysis_comparison(data, analysises_prev, analysises, names_dict):
    if analysises_prev:
        for analysis in analysises:
            name = analysis["indicator_id__name"]
            avg = analysises_prev.filter(indicator_id__name=name).aggregate(Avg("value"))[
                "value__avg"]
            changes = (analysis["value"] - avg) / avg * 100
            res = {
                "name": names_dict[name],
                "value": analysis["value"],
                "avg_prev_value": round(avg, 2),
                "interval_min": analysis["indicator_id__interval_min"],
                "interval_max": analysis["indicator_id__interval_max"],
                "unit": analysis["indicator_id__unit"],
                "changes": round(changes, 2)
            }
            data["analysis"].append(res)
    else:
        for analysis in analysises:
            name = analysis["indicator_id__name"]
            avg = None
            changes = None
            res = {
                "name": names_dict[name],
                "value": analysis["value"],
                "avg_prev_value": avg,
                "interval_min": analysis["indicator_id__interval_min"],
                "interval_max": analysis["indicator_id__interval_max"],
                "unit": analysis["indicator_id__unit"],
                "changes": changes
            }
            data["analysis"].append(res)

    return data
