# Generated by Django 3.1.1 on 2020-09-05 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20200903_0551'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='date',
            field=models.CharField(max_length=12, null=True),
        ),
    ]