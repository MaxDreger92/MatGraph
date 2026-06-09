from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("importing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="labelclassificationreport",
            name="file_link",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="labelclassificationreport",
            name="report_file_link",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="labelclassificationreport",
            name="file_name",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="attributeclassificationreport",
            name="file_link",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="attributeclassificationreport",
            name="report_file_link",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="attributeclassificationreport",
            name="file_name",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="nodeextractionreport",
            name="file_link",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="nodeextractionreport",
            name="report_file_link",
            field=models.CharField(default="None given", max_length=255),
        ),
        migrations.AlterField(
            model_name="nodeextractionreport",
            name="file_name",
            field=models.CharField(default="None given", max_length=255),
        ),
    ]
