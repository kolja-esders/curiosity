# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-22 14:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lake', '0005_askprice_is_express'),
    ]

    operations = [
        migrations.CreateModel(
            name='YubiKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50)),
                ('used', models.BooleanField(default=False)),
            ],
        ),
    ]
