from django.db import migrations, models
import django.db.models.deletion
import uuid

def populate_parent_rows(apps, schema_editor):
    db = schema_editor.connection.alias
    ImportProcess = apps.get_model('importing', 'ImportProcess')
    Process = apps.get_model('tasks', 'Process')

    for ip in ImportProcess.objects.using(db).all():
        process_id = getattr(ip, 'process_id', None) or f"migr-{uuid.uuid4()}"
        user_id = getattr(ip, 'user_id', None) or "unknown"

        p, created = Process.objects.using(db).get_or_create(
            id=ip.id,
            defaults={
                'process_id': process_id,
                'user_id': user_id,
                # status uses model default
                # error_message null OK
                # created_at/updated_at auto fields
            },
        )
        ip.process_ptr_id = p.id
        ip.save(update_fields=['process_ptr'])

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('importing', '0005_alter_importprocess_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='importprocess',
            name='process_ptr',
            field=models.OneToOneField(
                to='tasks.process',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                unique=True,
                parent_link=False,
                auto_created=True,
            ),
        ),
        migrations.RunPython(populate_parent_rows, migrations.RunPython.noop),

        migrations.RemoveField(
            model_name='importprocess',
            name='id',
        ),
        migrations.AlterField(
            model_name='importprocess',
            name='process_ptr',
            field=models.OneToOneField(
                to='tasks.process',
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                null=False,
                parent_link=True,
                auto_created=True,
            ),
        ),
    ]