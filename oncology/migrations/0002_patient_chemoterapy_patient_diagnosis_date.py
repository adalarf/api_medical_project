# Generated by Django 5.0.3 on 2024-06-07 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oncology', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='chemoterapy',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='diagnosis_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
