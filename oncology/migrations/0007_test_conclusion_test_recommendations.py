# Generated by Django 5.0.3 on 2024-05-19 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oncology', '0006_alter_patient_birth_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='conclusion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='test',
            name='recommendations',
            field=models.TextField(blank=True, null=True),
        ),
    ]
