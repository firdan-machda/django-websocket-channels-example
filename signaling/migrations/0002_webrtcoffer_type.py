# Generated by Django 4.2 on 2025-02-06 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signaling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webrtcoffer',
            name='type',
            field=models.CharField(default='offer', max_length=100),
        ),
    ]
