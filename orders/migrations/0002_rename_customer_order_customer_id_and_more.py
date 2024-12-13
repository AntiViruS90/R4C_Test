# Generated by Django 5.1.4 on 2024-12-13 10:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('robots', '0002_alter_robot_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='customer',
            new_name='customer_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='robot_serial',
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='order',
            name='is_fulfilled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='is_waiting',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='order',
            name='robot',
            field=models.ForeignKey(default=6, on_delete=django.db.models.deletion.CASCADE, to='robots.robot'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]