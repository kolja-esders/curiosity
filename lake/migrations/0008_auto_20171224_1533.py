# Generated by Django 2.0 on 2017-12-24 15:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lake', '0007_auto_20171223_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producer', models.CharField(max_length=32)),
                ('msg', models.CharField(max_length=256)),
                ('lvl', models.CharField(max_length=16)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='TradeSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_eur', models.FloatField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='log',
            name='trade_session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lake.TradeSession'),
        ),
    ]