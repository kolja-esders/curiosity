# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-15 16:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lake', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='volume_eur',
            field=models.FloatField(null=True),
        ),
    ]
