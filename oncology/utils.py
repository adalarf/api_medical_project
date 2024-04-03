import numpy as np
import matplotlib.pyplot as plt
from .models import Graphic, Indicator


def draw_hematological_research(values, patient_test):
    labels = np.array(['CD19/CD4', 'LYMF/CD19', 'NEU/LYMF', 'CD19/CD8'])
    values = np.array(values)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = np.concatenate((values, [values[0]]))
    angles += angles[:1]

    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    cd19_indicator = Indicator.objects.get(name='b_lymphocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')
    cd4_indicator = Indicator.objects.get(name='t_helpers')
    cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')
    min_indicator_values = [cd19_indicator.interval_min / cd4_indicator.interval_min,
                            lymf_indicator.interval_min / cd19_indicator.interval_min,
                            neu_indicator.interval_min / lymf_indicator.interval_min,
                            cd19_indicator.interval_min / cd8_indicator.interval_min]
    max_indicator_values = [cd19_indicator.interval_max / cd4_indicator.interval_max,
                            lymf_indicator.interval_max / cd19_indicator.interval_max,
                            neu_indicator.interval_max / lymf_indicator.interval_max,
                            cd19_indicator.interval_max / cd8_indicator.interval_max]
    min_indicator_values = np.array(min_indicator_values)
    max_indicator_values = np.array(max_indicator_values)
    min_angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    max_angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    min_indicator_values = np.concatenate((min_indicator_values, [min_indicator_values[0]]))
    min_angles += min_angles[:1]
    max_indicator_values = np.concatenate((max_indicator_values, [max_indicator_values[0]]))
    max_angles += max_angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})
    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    if Graphic.objects.exists():
        latest_graphic_id = Graphic.objects.latest('pk').pk + 1
    else:
        latest_graphic_id = 1
    file_path = f'media/hematological_research_{latest_graphic_id}.png'
    plt.savefig(file_path)
    graphic_instance = Graphic.objects.create(graphic=file_path, patient_test_id=patient_test)

    return graphic_instance.id