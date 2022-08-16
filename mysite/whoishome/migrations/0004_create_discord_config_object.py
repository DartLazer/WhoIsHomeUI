from django.db import migrations, models


def create_config(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    discord_config = apps.get_model("whoishome", "DiscordNotificationsConfig")
    discord_config.objects.using(db_alias).create(enabled_switch=False,
                                                  webhook_url=
                                                  "enter webhook url from server settings -> integrations -> webhooks",
                                                  arrival_message=
                                                  "{target} arrived home at {arrival_time} "
                                                  "after being away for {time_away}",
                                                  departure_message=
                                                  "{target} left home after at {departure_time} after "
                                                  "being home for {time_home}")



class Migration(migrations.Migration):
    dependencies = [
        ('whoishome', '0003_discordnotificationsconfig'),
    ]

    operations = [
        migrations.RunPython(create_config),
    ]
