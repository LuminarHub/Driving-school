# Generated by Django 5.2 on 2025-04-08 07:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0001_initial'),
        ('trainers', '0001_initial'),
        ('vehicles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_set', to='trainers.trainer'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='student',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='vehicles.vehicle'),
        ),
        migrations.AddField(
            model_name='studentpackage',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='students.student'),
        ),
        migrations.AddField(
            model_name='payment',
            name='student_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='students.studentpackage'),
        ),
        migrations.AddField(
            model_name='trainingpackage',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='students.course'),
        ),
        migrations.AddField(
            model_name='studentpackage',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.trainingpackage'),
        ),
        migrations.AddField(
            model_name='trainingsession',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='students.student'),
        ),
        migrations.AddField(
            model_name='trainingsession',
            name='student_package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.studentpackage'),
        ),
        migrations.AddField(
            model_name='trainingsession',
            name='trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessions_trainer', to='trainers.trainer'),
        ),
        migrations.AddField(
            model_name='trainingsession',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessions_vehicle', to='vehicles.vehicle'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='session',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='students.trainingsession'),
        ),
        migrations.AlterUniqueTogether(
            name='trainingsession',
            unique_together={('student', 'session_date', 'time_slot'), ('trainer', 'session_date', 'time_slot')},
        ),
    ]
