from django.db import migrations, models
import django.db.models.deletion
import whoishome.models


def create_default_device_types(apps, schema_editor):
    # Default device type icons included in the WhoIsHome installation
    device_types_icons = {
        "unknown": "question-circle",
        "pc": "pc-display-horizontal",
        "phone": "phone",
        "server": "server",
        "laptop": "laptop",
        "tv": "tv",
        "speaker": "speaker",
        "Smart Home Device": "house",
        "tablet": "tablet"
    }

    db_alias = schema_editor.connection.alias
    DeviceType = apps.get_model("whoishome", "DeviceType")

    # Creating each device type in the DeviceType table
    for device_type_name, icon_code in device_types_icons.items():
        DeviceType.objects.using(db_alias).create(
            name=device_type_name.title(),
            icon=icon_code.lower()
        )


def assign_device_type_foreign_keys(apps, schema_editor):
    Host = apps.get_model("whoishome", "Host")
    DeviceType = apps.get_model("whoishome", "DeviceType")

    # Assign each Host's device_type field by matching it to the DeviceType model
    for device_type_name in DeviceType.objects.values_list('name', flat=True):
        # Retrieve all Host instances with this device_type value
        device_type_instance = DeviceType.objects.get(name=device_type_name)
        Host.objects.filter(device_type=device_type_name.lower()).update(
            device_type_fk=device_type_instance
        )


class Migration(migrations.Migration):
    dependencies = [
        ('whoishome', '0015_delete_target_model'),  # Your latest migration
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('icon', models.CharField(default='question-circle', max_length=64)),
            ],
        ),
        migrations.RunPython(create_default_device_types),

        # Adding a new ForeignKey field temporarily on Host for migration
        migrations.AddField(
            model_name='host',
            name='device_type_fk',
            field=models.ForeignKey(
                to='whoishome.DeviceType',
                null=True,
                default=whoishome.models.get_default_device_type,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name='hosts'
            ),
        ),

        # Data migration to populate the ForeignKey field with corresponding DeviceType instances
        migrations.RunPython(assign_device_type_foreign_keys),

        # Remove the old CharField and rename the new ForeignKey
        migrations.RemoveField(
            model_name='host',
            name='device_type',
        ),
        migrations.RenameField(
            model_name='host',
            old_name='device_type_fk',
            new_name='device_type',
        ),
    ]
