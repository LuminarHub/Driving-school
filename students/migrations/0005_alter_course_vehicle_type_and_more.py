# Generated by Django 5.2 on 2025-04-11 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_alter_trainingsession_time_slot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='vehicle_type',
            field=models.CharField(choices=[('CAR', 'Car'), ('SCOOTY', 'Scooty'), ('OTHER', 'Other'), ('SCOOTY&CAR', 'SCOOTY & CAR')], max_length=10),
        ),
        migrations.AlterField(
            model_name='trainingpackage',
            name='vehicle_type',
            field=models.CharField(choices=[('CAR', 'Car'), ('SCOOTY', 'Scooty'), ('OTHER', 'Other'), ('SCOOTY&CAR', 'SCOOTY & CAR')], max_length=10),
        ),
    ]
