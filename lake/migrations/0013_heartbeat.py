# Generated by Django 2.0 on 2017-12-29 02:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lake', '0012_auto_20171225_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='Heartbeat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', models.CharField(max_length=64)),
                ('last_beat_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
