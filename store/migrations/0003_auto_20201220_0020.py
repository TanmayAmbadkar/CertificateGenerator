# Generated by Django 3.1.1 on 2020-12-19 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_tempcert'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tempcert',
            old_name='file',
            new_name='image',
        ),
        migrations.AddField(
            model_name='tempcert',
            name='csv',
            field=models.FileField(null=True, upload_to='csv/'),
        ),
    ]
