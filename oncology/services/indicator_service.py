from rest_framework.exceptions import NotFound
from oncology.models import Indicator
from .graphic_service import get_refs


def get_hematological_indicators():
    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    cd19_indicator = Indicator.objects.get(name='b_lymphocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')
    cd4_indicator = Indicator.objects.get(name='t_helpers')
    cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')

    hematological_indicators = {
        "lymf_indicator": lymf_indicator,
        "cd19_indicator": cd19_indicator,
        "neu_indicator": neu_indicator,
        "cd4_indicator": cd4_indicator,
        "cd8_indicator": cd8_indicator,
    }

    return hematological_indicators


def get_immune_indicators():
    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')
    cd4_indicator = Indicator.objects.get(name='t_helpers')
    cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')
    cd3_indicator = Indicator.objects.get(name='t_lymphocytes')

    immune_indicators = {
        "lymf_indicator": lymf_indicator,
        "neu_indicator": neu_indicator,
        "cd4_indicator": cd4_indicator,
        "cd8_indicator": cd8_indicator,
        "cd3_indicator": cd3_indicator,
    }

    return immune_indicators


def get_hematological_and_immune_indicators():
    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    cd19_indicator = Indicator.objects.get(name='b_lymphocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')
    cd4_indicator = Indicator.objects.get(name='t_helpers')
    cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')
    cd3_indicator = Indicator.objects.get(name='t_lymphocytes')

    hematological_and_immune_indicators = {
        "lymf_indicator": lymf_indicator,
        "cd19_indicator": cd19_indicator,
        "neu_indicator": neu_indicator,
        "cd4_indicator": cd4_indicator,
        "cd8_indicator": cd8_indicator,
        "cd3_indicator": cd3_indicator,
    }

    return hematological_and_immune_indicators


def get_regeneration_indicators():
    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    mon_indicator = Indicator.objects.get(name='monocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')

    regeneration_indicators = {
        "lymf_indicator": lymf_indicator,
        "mon_indicator": mon_indicator,
        "neu_indicator": neu_indicator,
    }

    return regeneration_indicators


def get_cytokine_indicators():
    cd3_il2_stimulated_indicator = Indicator.objects.get(name='cd3_il2_stimulated')
    cd3_il2_spontaneous_indicator = Indicator.objects.get(name='cd3_il2_spontaneous')
    cd3_tnfa_stimulated_indicator = Indicator.objects.get(name='cd3_tnfa_stimulated')
    cd3_tnfa_spontaneous_indicator = Indicator.objects.get(name='cd3_tnfa_spontaneous')
    cd3_ifny_stimulated_indicator = Indicator.objects.get(name='cd3_ifny_stimulated')
    cd3_ifny_spontaneous_indicator = Indicator.objects.get(name='cd3_ifny_spontaneous')

    cytokine_indicators = {
        "cd3_il2_stimulated_indicator": cd3_il2_stimulated_indicator,
        "cd3_il2_spontaneous_indicator": cd3_il2_spontaneous_indicator,
        "cd3_tnfa_stimulated_indicator": cd3_tnfa_stimulated_indicator,
        "cd3_tnfa_spontaneous_indicator": cd3_tnfa_spontaneous_indicator,
        "cd3_ifny_stimulated_indicator": cd3_ifny_stimulated_indicator,
        "cd3_ifny_spontaneous_indicator": cd3_ifny_spontaneous_indicator,
    }

    return cytokine_indicators


def get_value_and_indicator(j):
    value = j['value']
    indicator_name = j['indicator_name']
    try:
        indicator = Indicator.objects.get(name=indicator_name)
    except Indicator.DoesNotExist:
        raise NotFound('Indicator не существует')

    return value, indicator


def get_hematological_refs(hematological_indicators, scaled_deleter_values):
    return get_refs(
            [(hematological_indicators["cd19_indicator"], hematological_indicators["cd4_indicator"],
              scaled_deleter_values[0]),
             (hematological_indicators["lymf_indicator"], hematological_indicators["cd19_indicator"],
              scaled_deleter_values[1]),
             (hematological_indicators["neu_indicator"], hematological_indicators["lymf_indicator"],
              scaled_deleter_values[2]),
             (hematological_indicators["cd19_indicator"], hematological_indicators["cd8_indicator"],
              scaled_deleter_values[3])])


def get_immune_refs(immune_indicators, scaled_deleter_values):
    return get_refs([
        (immune_indicators["neu_indicator"], immune_indicators["cd4_indicator"], scaled_deleter_values[0]),
        (immune_indicators["neu_indicator"], immune_indicators["cd3_indicator"], scaled_deleter_values[1]),
        (immune_indicators["neu_indicator"], immune_indicators["lymf_indicator"], scaled_deleter_values[2]),
        (immune_indicators["neu_indicator"], immune_indicators["cd8_indicator"], scaled_deleter_values[3])])
