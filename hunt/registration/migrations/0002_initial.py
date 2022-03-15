# Generated by Django 3.2.8 on 2022-03-08 06:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hunt_registration', '0001_initial'),
        ('spoilr_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userauth',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teamregistrationinfo',
            name='team',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
    ]
