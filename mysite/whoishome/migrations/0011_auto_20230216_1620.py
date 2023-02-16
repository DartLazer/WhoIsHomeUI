# Generated by Django 3.2.18 on 2023-02-16 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whoishome', '0010_auto_20230216_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='discordnotificationsconfig',
            name='curfew_message',
            field=models.CharField(default='At time {arrival_time} device {target} connected during curfew time', max_length=500),
        ),
        migrations.AddField(
            model_name='emailconfig',
            name='curfew_message',
            field=models.CharField(default='At time {arrival_time} device {target} connected during curfew time', max_length=500),
        ),
        migrations.AddField(
            model_name='emailconfig',
            name='curfew_subject',
            field=models.CharField(default='{target} connected during curfew.', max_length=500),
        ),
    ]
