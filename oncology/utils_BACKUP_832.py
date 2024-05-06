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


def save_graphic(graphic_name, patient_test):
    if Graphic.objects.exists():
        latest_graphic_id = Graphic.objects.latest('pk').pk + 1
    else:
        latest_graphic_id = 1
    file_path = f'media/{graphic_name}_{latest_graphic_id}.png'
    plt.savefig(file_path)
    graphic_instance = Graphic.objects.create(graphic=file_path, patient_test_id=patient_test)
    return graphic_instance.id


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

    graphic = save_graphic('hematological_research', patient_test)

    return graphic


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

    draw_scaled_marks([0.04, 1.2, '1.0'], [0.02, 2.2, '2.0'], [0.015, 3.2, '3.0'], [0.01, 4.2, '4.0'],
                      [-1.33, 0.95, '2.6'], [-1.46, 1.95, '5.2'], [-1.50, 2.95, '7.8'], [-1.515, 3.95, '10.4'],
                      [-3.2, 0.8, '0.4'], [-3.17, 1.8, '0.8'], [-3.16, 2.8, '1.2'], [-3.155, 3.8, '1.6'],
                      [1.375, 1.05, '0.8'], [1.46, 2.05, '1.6'], [1.5, 3.05, '2.4'], [1.52, 4.05, '3.2'])

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

    graphic = save_graphic('immune_status', patient_test)

    return graphic


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

    angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in angles]
    min_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in min_angles]
    max_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in max_angles]

    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    draw_scaled_marks([-0.47, 1.3, '24.0'], [-0.478, 2.3, '48.0'], [-0.489, 3.3, '72.0'], [-0.502, 4.3, '96.0'],
                      [-2.3, 0.95, '24.0'], [-2.465, 1.95, '48.0'], [-2.51, 2.95, '72.0'], [-2.54, 3.95, '96.0'],
                      # [-5.06, 1.1, '24.0'], [-4.35, 2.1, '48.0'], [-4.3, 3.1, '72.0'], [-4.25, 4.1, '96.0'])
                      [1.3, 1.05, '24.0'], [1.428, 2.05, '48.0'], [1.467, 3.05, '72.0'], [1.488, 4.05, '96.0'])

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

    # ax.set_theta_offset(np.pi * 20)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic('cytokine_status', patient_test)

    return graphic

<<<<<<< HEAD
=======


def draw_regeneration_type(values, patient_test):
    labels = np.array(['Лимфоциты/моноциты', 'Нейтрофилы/лимфоциты', 'Нейтрофилы/моноциты'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(28.5), values[1] / Decimal(0.58), values[2] / Decimal(42.8)]
    values, angles = make_usable_values(values_scaled, labels)

    lymf_indicator = Indicator.objects.get(name='lymphocytes')
    mon_indicator = Indicator.objects.get(name='monocytes')
    neu_indicator = Indicator.objects.get(name='neutrophils')

    min_indicator_values, max_indicator_values = get_refs([(lymf_indicator, mon_indicator, 28.5),
                                                           (neu_indicator, lymf_indicator, 0.58),
                                                           (neu_indicator, mon_indicator, 42.8)])

    # min_indicator_values = [Decimal(6) / Decimal(28.5),
    #                         Decimal(1.67) / Decimal(0.58),
    #                         Decimal(10) / Decimal(42.8)]
    # max_indicator_values = [Decimal(100) / Decimal(28.5),
    #                         Decimal(1.8) / Decimal(0.58),
    #                         Decimal(180) / Decimal(42.8)]

    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)


    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})

    angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in angles]
    min_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in min_angles]
    max_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in max_angles]

    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    draw_scaled_marks([-0.47, 1.3, '28.5'], [-0.478, 2.3, '57.0'], [-0.489, 3.3, '85.5'], [-0.502, 4.3, '142.5'],
                      [1.3, 1.05, '0.58'], [1.428, 2.05, '1.16'], [1.467, 3.05, '1.74'], [1.488, 4.05, '2.32'],
                      [-2.3, 0.95, '42.8'], [-2.465, 1.95, '85.6'], [-2.51, 2.95, '128.4'], [-2.54, 3.95, '180.2'])

    draw_values(angles, values, values_not_scaled, ax)

    min_values_not_scaled, max_values_not_scaled = get_refs([(lymf_indicator, mon_indicator, None),
                                                             (neu_indicator, lymf_indicator, None),
                                                             (neu_indicator, mon_indicator, None)])

    # min_values_not_scaled = [Decimal(6), Decimal(1.67), Decimal(10)]
    # max_values_not_scaled = [Decimal(100), Decimal(1.8), Decimal(180)]

    min_values_not_scaled = make_usable_values(min_values_not_scaled)
    max_values_not_scaled = make_usable_values(max_values_not_scaled)


    draw_values(min_angles, min_indicator_values, min_values_not_scaled, ax)
    draw_values(max_angles, max_indicator_values, max_values_not_scaled, ax)

    ax.set_yticks([1,2,3,4,5])
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic('regeneration_type', patient_test)

    return graphic



def draw_regeneration_type1(values, patient_test):
    labels = np.array(['Лимфоциты/моноциты', 'Нейтрофилы/лимфоциты', 'Нейтрофилы/моноциты'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(2), values[1] / Decimal(0.58), values[2] / Decimal(3)]
    values, angles = make_usable_values(values_scaled, labels)

    min_indicator_values = [Decimal(3.4) / Decimal(2),
                            Decimal(1.89) / Decimal(0.58),
                            Decimal(6.4) / Decimal(3)]
    max_indicator_values = [Decimal(6.1) / Decimal(2),
                            Decimal(2.1) / Decimal(0.58),
                            Decimal(12.8) / Decimal(3)]

    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)


    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})

    angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in angles]
    min_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in min_angles]
    max_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in max_angles]

    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    draw_scaled_marks([-0.47, 1.3, '1.85'], [-0.478, 2.3, '3.7'], [-0.489, 3.3, '5.55'], [-0.502, 4.3, '7.4'],
                      [1.3, 1.05, '0.58'], [1.428, 2.05, '1.16'], [1.467, 3.05, '1.74'], [1.488, 4.05, '2.32'],
                      [-2.3, 0.95, '3.0'], [-2.465, 1.95, '6.0'], [-2.51, 2.95, '9.0'], [-2.54, 3.95, '12.0'])

    draw_values(angles, values, values_not_scaled, ax)

    min_values_not_scaled = [Decimal(3.4), Decimal(1.89), Decimal(6.4)]
    max_values_not_scaled = [Decimal(6.1), Decimal(2.1), Decimal(12.8)]

    min_values_not_scaled = make_usable_values(min_values_not_scaled)
    max_values_not_scaled = make_usable_values(max_values_not_scaled)


    draw_values(min_angles, min_indicator_values, min_values_not_scaled, ax)
    draw_values_with_other_angle(max_angles, max_indicator_values, max_values_not_scaled, ax)

    ax.set_yticks([1,2,3,4,5])
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic('regeneration_type', patient_test)

    return graphic

>>>>>>> hw6
