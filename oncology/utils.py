import numpy as np
import matplotlib.pyplot as plt
from .models import Graphic, Indicator


def get_indicator_values(first, second, val):
   min = first.interval_min / second.interval_min / val
   max = first.interval_max / second.interval_max / val
   if max > min:
       return min, max
   return max, min

def get_refs(refs):
    min_refs = []
    max_refs = []
    for ref in refs:
        min, max = get_indicator_values(ref[0], ref[1], ref[2])
        min_refs.append(min)
        max_refs.append(max)
    return min_refs, max_refs


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
    min_indicator_values, max_indicator_values = get_refs([(cd19_indicator, cd4_indicator, 0.2),
              (lymf_indicator, cd19_indicator, 2),
              (neu_indicator, lymf_indicator, 0.4),
              (cd19_indicator, cd8_indicator, 0.2)])
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

    plt.text(0.04, 1.2, '0.2', fontsize=8, color='black', ha='center')
    plt.text(0.02, 2.2, '0.4', fontsize=8, color='black', ha='center')
    plt.text(0.015, 3.2, '0.6', fontsize=8, color='black', ha='center')
    plt.text(0.01, 4.2, '0.8', fontsize=8, color='black', ha='center')

    plt.text(-1.33, 0.95, '0.2', fontsize=8, color='black', ha='center')
    plt.text(-1.46, 1.95, '0.4', fontsize=8, color='black', ha='center')
    plt.text(-1.50, 2.95, '0.6', fontsize=8, color='black', ha='center')
    plt.text(-1.515, 3.95, '0.8', fontsize=8, color='black', ha='center')

    plt.text(-3.2, 0.8, '0.4', fontsize=8, color='black', ha='center')
    plt.text(-3.17, 1.8, '0.8', fontsize=8, color='black', ha='center')
    plt.text(-3.16, 2.8, '1.2', fontsize=8, color='black', ha='center')
    plt.text(-3.155, 3.8, '1.6', fontsize=8, color='black', ha='center')

    plt.text(1.375, 1.05, '2.0', fontsize=8, color='black', ha='center')
    plt.text(1.46, 2.05, '4.0', fontsize=8, color='black', ha='center')
    plt.text(1.5, 3.05, '6.0', fontsize=8, color='black', ha='center')
    plt.text(1.52, 4.05, '8.0', fontsize=8, color='black', ha='center')

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    if Graphic.objects.exists():
        latest_graphic_id = Graphic.objects.latest('pk').pk + 1
    else:
        latest_graphic_id = 1
    file_path = f'media/hematological_research_{latest_graphic_id}.png'
    plt.savefig(file_path)
    graphic_instance = Graphic.objects.create(graphic=file_path, patient_test_id=patient_test)

    return graphic_instance.id