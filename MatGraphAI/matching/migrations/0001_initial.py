# Generated by Django 3.2.16 on 2024-01-31 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MatchingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=60)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('report', models.TextField()),
            ],
            options={
                'verbose_name': 'Matching Report',
                'verbose_name_plural': 'Matching Reports',
            },
        ),
    ]
