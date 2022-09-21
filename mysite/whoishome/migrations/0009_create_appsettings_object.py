from django.db import migrations, models


def create_config(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    app_settings_config = apps.get_model("whoishome", "AppSettings")
    app_settings_config.objects.using(db_alias).create(login_required=False, )


class Migration(migrations.Migration):
    dependencies = [
        ('whoishome', '0008_appsettings'),
    ]

    operations = [
        migrations.RunPython(create_config),
    ]
