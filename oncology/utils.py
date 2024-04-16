import decimal

import numpy as np
import matplotlib.pyplot as plt
from .models import Graphic, Indicator
from decimal import Decimal


def get_indicator_values(first, second, val):
   if val is None:
       min = first.interval_min / second.interval_min
       max = first.interval_max / second.interval_max
   else:
       min = first.interval_min / second.interval_min / Decimal(val)
       max = first.interval_max / second.interval_max / Decimal(val)
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


def draw_values(angles, values, values_not_scaled, ax):
    for i, angle in enumerate(angles):
        y = values[i]

        x_arrow = angle
        y_arrow = y

        ax.annotate(str(values_not_scaled[i])[0:4], fontsize=8, xy=(x_arrow, y_arrow), xytext=(Decimal(x_arrow) + Decimal(0.35), Decimal(y_arrow) + Decimal(0.15)),
                    arrowprops=dict(arrowstyle="->", color='black'))


def draw_values_with_other_angle(angles, values, values_not_scaled, ax):
    for i, angle in enumerate(angles):
        y = values[i]

        x_arrow = angle
        y_arrow = y

        ax.annotate(str(values_not_scaled[i])[0:4], fontsize=8, xy=(x_arrow, y_arrow), xytext=(Decimal(x_arrow) + Decimal(0.30), Decimal(y_arrow) + Decimal(0.35)),
                    arrowprops=dict(arrowstyle="->", color='black'))


def make_usable_values(values, labels=None):
    values = np.array(values)
    values = np.concatenate((values, [values[0]]))
    if labels is not None:
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        return values, angles
    return values


def draw_scaled_marks(*mark_values):
    for mark in mark_values:
        plt.text(mark[0], mark[1], mark[2], fontsize=8, color='black', ha='center')


def draw_hematological_research(values, patient_test):
    labels = np.array(['CD19/CD4', 'LYMF/CD19', 'NEU/LYMF', 'CD19/CD8'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(0.2), values[1] / Decimal(2), values[2] / Decimal(0.4), values[3] / Decimal(0.2)]
    values, angles = make_usable_values(values_scaled, labels)

    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    cd19_indicator = Indicator.objects.get(name='b_lymphocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')
    cd4_indicator = Indicator.objects.get(name='t_helpers')
    cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')
    min_indicator_values, max_indicator_values = get_refs([(cd19_indicator, cd4_indicator, 0.2),
              (lymf_indicator, cd19_indicator, 2),
              (neu_indicator, lymf_indicator, 0.4),
              (cd19_indicator, cd8_indicator, 0.2)])
    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})
    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    draw_scaled_marks([0.04, 1.2, '0.2'], [0.02, 2.2, '0.4'], [0.015, 3.2, '0.6'], [0.01, 4.2, '0.8'],
                      [-1.33, 0.95, '0.2'], [-1.46, 1.95, '0.4'], [-1.50, 2.95, '0.6'], [-1.515, 3.95, '0.8'],
                      [-3.2, 0.8, '0.4'], [-3.17, 1.8, '0.8'], [-3.16, 2.8, '1.2'], [-3.155, 3.8, '1.6'],
                      [1.375, 1.05, '2.0'], [1.46, 2.05, '4.0'], [1.5, 3.05, '6.0'], [1.52, 4.05, '8.0'])

    draw_values(angles, values, values_not_scaled, ax)

    min_values_not_scaled, max_values_not_scaled = get_refs([(cd19_indicator, cd4_indicator, None),
                                                           (lymf_indicator, cd19_indicator, None),
                                                           (neu_indicator, lymf_indicator, None),
                                                           (cd19_indicator, cd8_indicator, None)])
    min_values_not_scaled = make_usable_values(min_values_not_scaled)
    max_values_not_scaled = make_usable_values(max_values_not_scaled)

    draw_values(min_angles, min_indicator_values, min_values_not_scaled, ax)
    draw_values_with_other_angle(max_angles, max_indicator_values, max_values_not_scaled, ax)

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


def draw_immune_status(values, patient_test):
    labels = np.array(['NEU/CD4', 'NEU/CD3', 'NEU/LYMF', 'NEU/CD8'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(1.0), values[1] / Decimal(0.8), values[2] / Decimal(0.4),
                     values[3] / Decimal(2.6)]
    values, angles = make_usable_values(values_scaled, labels)

    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')
    cd4_indicator = Indicator.objects.get(name='t_helpers')
    cd8_indicator = Indicator.objects.get(name='t_cytotoxic_lymphocytes')
    cd3_indicator = Indicator.objects.get(name='t_lymphocytes')

    min_indicator_values, max_indicator_values = get_refs([(neu_indicator, cd4_indicator, 1),
                                                           (neu_indicator, cd3_indicator, 0.8),
                                                           (neu_indicator, lymf_indicator, 0.4),
                                                           (neu_indicator, cd8_indicator, 2.6)])
    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})
    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    plt.text(0.04, 1.2, '1.0', fontsize=8, color='black', ha='center')
    plt.text(0.02, 2.2, '2.0', fontsize=8, color='black', ha='center')
    plt.text(0.015, 3.2, '3.0', fontsize=8, color='black', ha='center')
    plt.text(0.01, 4.2, '4.0', fontsize=8, color='black', ha='center')

    plt.text(-1.33, 0.95, '2.6', fontsize=8, color='black', ha='center')
    plt.text(-1.46, 1.95, '5.2', fontsize=8, color='black', ha='center')
    plt.text(-1.50, 2.95, '7.8', fontsize=8, color='black', ha='center')
    plt.text(-1.515, 3.95, '10.4', fontsize=8, color='black', ha='center')

    plt.text(-3.2, 0.8, '0.4', fontsize=8, color='black', ha='center')
    plt.text(-3.17, 1.8, '0.8', fontsize=8, color='black', ha='center')
    plt.text(-3.16, 2.8, '1.2', fontsize=8, color='black', ha='center')
    plt.text(-3.155, 3.8, '1.6', fontsize=8, color='black', ha='center')

    plt.text(1.375, 1.05, '0.8', fontsize=8, color='black', ha='center')
    plt.text(1.46, 2.05, '1.6', fontsize=8, color='black', ha='center')
    plt.text(1.5, 3.05, '2.4', fontsize=8, color='black', ha='center')
    plt.text(1.52, 4.05, '3.2', fontsize=8, color='black', ha='center')

    draw_values(angles, values, values_not_scaled, ax)

    min_values_not_scaled, max_values_not_scaled = get_refs([(neu_indicator, cd4_indicator, None),
                                                             (neu_indicator, cd3_indicator, None),
                                                             (neu_indicator, lymf_indicator, None),
                                                             (neu_indicator, cd8_indicator, None)])

    min_values_not_scaled = make_usable_values(min_values_not_scaled)
    max_values_not_scaled = make_usable_values(max_values_not_scaled)

    draw_values(min_angles, min_indicator_values, min_values_not_scaled, ax)
    draw_values(max_angles, max_indicator_values, max_values_not_scaled, ax)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    if Graphic.objects.exists():
        latest_graphic_id = Graphic.objects.latest('pk').pk + 1
    else:
        latest_graphic_id = 1
    file_path = f'media/immune_status_{latest_graphic_id}.png'
    plt.savefig(file_path)
    graphic_instance = Graphic.objects.create(graphic=file_path, patient_test_id=patient_test)

    return graphic_instance.id


def draw_cytokine_status(values, patient_test):
    labels = np.array(['Интерликин', 'ФНО', 'Интерферон'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(24.0), values[1] / Decimal(24.0), values[2] / Decimal(24.0)]
    values, angles = make_usable_values(values_scaled, labels)

    # cd3_il2_stimulated_indicator = Indicator.objects.get(name='cd3_il2_stimulated')
    # cd3_il2_spontaneous_indicator = Indicator.objects.get(name='cd3_il2_spontaneous')
    #
    # cd3_tnfa_stimulated_indicator = Indicator.objects.get(name='cd3_tnfa_stimulated')
    # cd3_tnfa_spontaneous_indicator = Indicator.objects.get(name='cd3_tnfa_spontaneous')
    #
    # cd3_ifny_stimulated_indicator = Indicator.objects.get(name='cd3_ifny_stimulated')
    # cd3_ifny_spontaneous_indicator = Indicator.objects.get(name='cd3_ifny_spontaneous')
    #
    # min_indicator_values, max_indicator_values = get_refs(
    #     [(cd3_il2_stimulated_indicator, cd3_il2_spontaneous_indicator, 24.0),
    #      (cd3_tnfa_stimulated_indicator, cd3_tnfa_spontaneous_indicator, 24.0),
    #      (cd3_ifny_stimulated_indicator, cd3_ifny_spontaneous_indicator, 24.0)])

    min_indicator_values = [80 / Decimal(24.0), 80 / Decimal(24.0), 80 / Decimal(24.0)]
    max_indicator_values = [120 / Decimal(24.0), 120 / Decimal(24.0), 120 / Decimal(24.0)]
    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})

    # angles = [(angle - (angle / 3)) % (2 * np.pi) for angle in angles]
    # min_angles = [(angle - (angle / 3)) % (2 * np.pi) for angle in min_angles]
    # max_angles = [(angle - (angle / 3)) % (2 * np.pi) for angle in max_angles]

    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    draw_scaled_marks([0.04, 1.3, '24.0'], [0.02, 2.3, '48.0'], [0.015, 3.3, '72.0'], [0.01, 4.3, '96.0'],
                      [-1.75, 0.95, '24.0'], [-1.9, 1.95, '48.0'], [-1.96, 2.95, '72.0'], [-1.97, 3.95, '96.0'],
                      [-4.5, 1.0, '24.0'], [-4.35, 2.0, '48.0'], [-4.3, 3.0, '72.0'], [-4.25, 4.0, '96.0'])

    draw_values(angles, values, values_not_scaled, ax)

    # min_values_not_scaled, max_values_not_scaled = get_refs(
    #     [(cd3_il2_stimulated_indicator, cd3_il2_spontaneous_indicator, None),
    #      (cd3_tnfa_stimulated_indicator, cd3_tnfa_spontaneous_indicator, None),
    #      (cd3_ifny_stimulated_indicator, cd3_ifny_spontaneous_indicator, None)])

    min_values_not_scaled = [80, 80, 80]
    max_values_not_scaled = [120, 120, 120]

    min_values_not_scaled = make_usable_values(min_values_not_scaled)
    max_values_not_scaled = make_usable_values(max_values_not_scaled)

    draw_values(min_angles, min_indicator_values, min_values_not_scaled, ax)
    draw_values(max_angles, max_indicator_values, max_values_not_scaled, ax)

    #ax.set_theta_offset(np.pi * 16)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    if Graphic.objects.exists():
        latest_graphic_id = Graphic.objects.latest('pk').pk + 1
    else:
        latest_graphic_id = 1
    file_path = f'media/cytokine_status_{latest_graphic_id}.png'
    plt.savefig(file_path)
    graphic_instance = Graphic.objects.create(graphic=file_path, patient_test_id=patient_test)

    return graphic_instance.id


