# Generated by Django 3.2.9 on 2021-11-30 16:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('whoishome', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='logdata',
            name='time_saved',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='DateTime Last edited'),
        ),
    ]
