# Generated by Django 4.2.5 on 2023-09-29 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_rename_description_event_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
