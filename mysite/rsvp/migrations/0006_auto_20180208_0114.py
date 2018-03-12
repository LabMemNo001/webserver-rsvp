# Generated by Django 2.0.1 on 2018-02-08 01:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rsvp', '0005_auto_20180207_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_content',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='event',
            name='guest',
            field=models.ManyToManyField(related_name='guest', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='vendor',
            field=models.ManyToManyField(related_name='vendor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='owner',
            field=models.ManyToManyField(related_name='owner', to=settings.AUTH_USER_MODEL),
        ),
    ]