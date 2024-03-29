# Generated by Django 3.2.18 on 2023-02-16 14:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whoishome', '0009_create_appsettings_object'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsettings',
            name='curfew_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='curfew_end_time',
            field=models.TimeField(blank=True, default=datetime.time(8, 0)),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='curfew_start_time',
            field=models.TimeField(blank=True, default=datetime.time(22, 0)),
        ),
        migrations.AddField(
            model_name='host',
            name='kid_curfew_mode',
            field=models.BooleanField(default=False),
        ),
    ]
