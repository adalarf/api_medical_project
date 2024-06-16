import numpy as np
import matplotlib.pyplot as plt
from oncology.models import Graphic
from .indicator_service import get_hematological_indicators, get_immune_indicators, get_hematological_refs,\
    get_immune_refs
from decimal import Decimal
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg
import boto3
from django.conf import settings
from django.db.models import Q


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


def get_s3_and_bucket_name():
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                      region_name=settings.AWS_S3_REGION_NAME)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    return s3, bucket_name


def save_graphic(fig, graphic_name, patient_test, latest_graphic_id=None):
    if latest_graphic_id is None:
        latest_graphic_id = 1
        if Graphic.objects.exists():
            latest_graphic_id = Graphic.objects.latest('pk').pk + 1

    file_path = f'{graphic_name}_{latest_graphic_id}.png'
    canvas = FigureCanvasAgg(fig)
    buffer = BytesIO()
    canvas.print_png(buffer)
    buffer.seek(0)

    s3, bucket_name = get_s3_and_bucket_name()
    s3.upload_fileobj(buffer, bucket_name, file_path)
    graphic_instance = Graphic.objects.create(id=latest_graphic_id, graphic=file_path, patient_test_id=patient_test)

    return graphic_instance.id


def delete_graphic(graphics_to_delete):
    s3, bucket_name = get_s3_and_bucket_name()
    for graphic in graphics_to_delete:
        s3.delete_object(Bucket=bucket_name, Key=graphic.graphic.name)

    graphics_to_delete.delete()


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


def draw_figure_and_axis(angles, values, min_angles, max_angles, min_indicator_values, max_indicator_values):
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})
    ax.plot(angles, values, color='red', linewidth=2)
    ax.plot(min_angles, min_indicator_values, linestyle='--', color='green', linewidth=2)
    ax.plot(max_angles, max_indicator_values, linestyle='--', color='green', linewidth=2)

    return fig, ax


def draw_refs(ax, min_angles, max_angles, min_indicator_values, max_indicator_values,
              min_values_not_scaled, max_values_not_scaled):
    min_values_not_scaled = make_usable_values(min_values_not_scaled)
    max_values_not_scaled = make_usable_values(max_values_not_scaled)

    draw_values(min_angles, min_indicator_values, min_values_not_scaled, ax)
    draw_values_with_other_angle(max_angles, max_indicator_values, max_values_not_scaled, ax)


def draw_hematological_research(values, patient_test, latest_graphic_id=None):
    labels = np.array(['CD19/CD4', 'LYMF/CD19', 'NEU/LYMF', 'CD19/CD8'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(0.2), values[1] / Decimal(2), values[2] / Decimal(0.4), values[3] / Decimal(0.2)]
    values, angles = make_usable_values(values_scaled, labels)

    hematological_indicators = get_hematological_indicators()

    min_indicator_values, max_indicator_values = get_hematological_refs(hematological_indicators, [0.2, 2, 0.4, 0.2])

    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)

    fig, ax = draw_figure_and_axis(angles, values, min_angles, max_angles, min_indicator_values, max_indicator_values)

    draw_scaled_marks([0.04, 1.2, '0.2'], [0.02, 2.2, '0.4'], [0.015, 3.2, '0.6'], [0.01, 4.2, '0.8'],
                      [-1.33, 0.95, '0.2'], [-1.46, 1.95, '0.4'], [-1.50, 2.95, '0.6'], [-1.515, 3.95, '0.8'],
                      [-3.2, 0.8, '0.4'], [-3.17, 1.8, '0.8'], [-3.16, 2.8, '1.2'], [-3.155, 3.8, '1.6'],
                      [1.375, 1.05, '2.0'], [1.46, 2.05, '4.0'], [1.5, 3.05, '6.0'], [1.52, 4.05, '8.0'])

    draw_values(angles, values, values_not_scaled, ax)

    draw_refs(ax, min_angles, max_angles, min_indicator_values, max_indicator_values,
              *get_hematological_refs(hematological_indicators, [None, None, None, None]))

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic(fig, 'hematological_research', patient_test, latest_graphic_id)

    return graphic


def draw_immune_status(values, patient_test, latest_graphic_id=None):
    labels = np.array(['NEU/CD4', 'NEU/CD3', 'NEU/LYMF', 'NEU/CD8'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(1.0), values[1] / Decimal(0.8), values[2] / Decimal(0.4),
                     values[3] / Decimal(2.6)]
    values, angles = make_usable_values(values_scaled, labels)

    immune_indicators = get_immune_indicators()

    min_indicator_values, max_indicator_values = get_immune_refs(immune_indicators, [1, 0.8, 0.4, 2.6])

    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)

    fig, ax = draw_figure_and_axis(angles, values, min_angles, max_angles, min_indicator_values, max_indicator_values)

    draw_scaled_marks([0.04, 1.2, '1.0'], [0.02, 2.2, '2.0'], [0.015, 3.2, '3.0'], [0.01, 4.2, '4.0'],
                      [-1.33, 0.95, '2.6'], [-1.46, 1.95, '5.2'], [-1.50, 2.95, '7.8'], [-1.515, 3.95, '10.4'],
                      [-3.2, 0.8, '0.4'], [-3.17, 1.8, '0.8'], [-3.16, 2.8, '1.2'], [-3.155, 3.8, '1.6'],
                      [1.375, 1.05, '0.8'], [1.46, 2.05, '1.6'], [1.5, 3.05, '2.4'], [1.52, 4.05, '3.2'])

    draw_values(angles, values, values_not_scaled, ax)

    draw_refs(ax, min_angles, max_angles, min_indicator_values, max_indicator_values,
              *get_immune_refs(immune_indicators, [None, None, None, None]))

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic(fig, 'immune_status', patient_test, latest_graphic_id)

    return graphic


def draw_cytokine_status(values, patient_test, latest_graphic_id=None):
    labels = np.array(['Интерликин', 'ФНО', 'Интерферон'])
    values_not_scaled = make_usable_values(values)
    values_scaled = [values[0] / Decimal(24.0), values[1] / Decimal(24.0), values[2] / Decimal(24.0)]
    values, angles = make_usable_values(values_scaled, labels)

    min_indicator_values = [80 / Decimal(24.0), 80 / Decimal(24.0), 80 / Decimal(24.0)]
    max_indicator_values = [120 / Decimal(24.0), 120 / Decimal(24.0), 120 / Decimal(24.0)]
    min_indicator_values, min_angles = make_usable_values(min_indicator_values, labels)
    max_indicator_values, max_angles = make_usable_values(max_indicator_values, labels)

    angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in angles]
    min_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in min_angles]
    max_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in max_angles]

    fig, ax = draw_figure_and_axis(angles, values, min_angles, max_angles, min_indicator_values, max_indicator_values)

    draw_scaled_marks([-0.47, 1.3, '24.0'], [-0.478, 2.3, '48.0'], [-0.489, 3.3, '72.0'], [-0.502, 4.3, '96.0'],
                      [-2.3, 0.95, '24.0'], [-2.465, 1.95, '48.0'], [-2.51, 2.95, '72.0'], [-2.54, 3.95, '96.0'],
                      [1.3, 1.05, '24.0'], [1.428, 2.05, '48.0'], [1.467, 3.05, '72.0'], [1.488, 4.05, '96.0'])

    draw_values(angles, values, values_not_scaled, ax)

    draw_refs(ax, min_angles, max_angles, min_indicator_values, max_indicator_values,
              [80, 80, 80], [120, 120, 120])

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic(fig, 'cytokine_status', patient_test, latest_graphic_id)

    return graphic


def draw_regeneration_type1(values, patient_test, latest_graphic_id=None):
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

    angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in angles]
    min_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in min_angles]
    max_angles = [(angle - np.pi / 6) % (2 * np.pi) for angle in max_angles]

    fig, ax = draw_figure_and_axis(angles, values, min_angles, max_angles, min_indicator_values, max_indicator_values)

    draw_scaled_marks([-0.47, 1.3, '1.85'], [-0.478, 2.3, '3.7'], [-0.489, 3.3, '5.55'], [-0.502, 4.3, '7.4'],
                      [1.3, 1.05, '0.58'], [1.428, 2.05, '1.16'], [1.467, 3.05, '1.74'], [1.488, 4.05, '2.32'],
                      [-2.3, 0.95, '3.0'], [-2.465, 1.95, '6.0'], [-2.51, 2.95, '9.0'], [-2.54, 3.95, '12.0'])

    draw_values(angles, values, values_not_scaled, ax)

    draw_refs(ax, min_angles, max_angles, min_indicator_values, max_indicator_values,
              [Decimal(3.4), Decimal(1.89), Decimal(6.4)], [Decimal(6.1), Decimal(2.1), Decimal(12.8)])

    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    labels_l = ('Результаты', 'Нижние референтные значения', 'Верхние референтные значения')
    ax.legend(labels_l, labelspacing=0.1, fontsize='small')

    graphic = save_graphic(fig, 'regeneration_type', patient_test, latest_graphic_id)

    return graphic


def recreate_regeneration_or_cytokine_graphic(test, test_type, analysis, patient_test):
    graphic_id = Graphic.objects.get(patient_test_id=test.patient_test_id,
                                     graphic__startswith=test_type).id
    graphics_to_delete = Graphic.objects.filter(patient_test_id=test.patient_test_id,
                                                graphic__startswith=test_type)
    delete_graphic(graphics_to_delete)

    if test_type == 'regeneration_type':
        draw_regeneration_type1(analysis, patient_test, graphic_id)
    else:
        draw_cytokine_status(analysis, patient_test, graphic_id)


def recreate_hematological_and_immune_graphic(test, test_type, hematological_and_immune_analysis, patient_test):
    graphic_id = Graphic.objects.get(patient_test_id=test.patient_test_id,
                                     graphic__startswith=test_type).id
    if test_type == 'hematological_research':
        immune_graphic_id = Graphic.objects.get(patient_test_id=test.patient_test_id,
                                                graphic__startswith='immune_status').id
    else:
        immune_graphic_id = Graphic.objects.get(patient_test_id=test.patient_test_id,
                                                graphic__startswith='hematological_research').id
    Graphic.objects.filter(Q(patient_test_id=test.patient_test_id),
                           Q(graphic__startswith='hematological_research')
                           | Q(graphic__startswith='immune_status')).delete()
    graphics_to_delete = Graphic.objects.filter(Q(patient_test_id=test.patient_test_id),
                                                Q(graphic__startswith='hematological_research')
                                                | Q(graphic__startswith='immune_status'))
    delete_graphic(graphics_to_delete)

    draw_hematological_research(hematological_and_immune_analysis["hematological_analysis"],
                                patient_test, graphic_id)

    draw_immune_status(hematological_and_immune_analysis["immune_analysis"],
                       patient_test, immune_graphic_id)


def get_graphics_by_patient_test_id(patient_test_id):
    return Graphic.objects.filter(patient_test_id=patient_test_id)
