from django.db import migrations, models


def create_default_telegram_config(apps, schema_editor):
    TelegramNotificationsConfig = apps.get_model('whoishome', 'TelegramNotificationsConfig')
    default_config = TelegramNotificationsConfig(
        enabled_switch=False,
        bot_token="",
        chat_id="",
        arrival_message="",
        departure_message="",
        curfew_message='At time {arrival_time} device {target} connected during curfew time',
        new_connection_message='At time {arrival_time} a new device connected '
                               'to the network\n'
                               'MAC: {mac}\n'
                               'IP: {ip}\n'
                               'Name: {name}'
    )
    default_config.save()


class Migration(migrations.Migration):
    dependencies = [
        ('whoishome', '0012_telegramnotificationsconfig_and_more'),  # Replace with the name of your previous migration
    ]

    operations = [
        migrations.RunPython(create_default_telegram_config),
    ]
