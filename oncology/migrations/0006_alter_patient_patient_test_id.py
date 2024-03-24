# Generated by Django 5.0.3 on 2024-03-24 06:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oncology', '0005_alter_patient_diagnosis_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='patient_test_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='oncology.patienttests'),
        ),
    ]
