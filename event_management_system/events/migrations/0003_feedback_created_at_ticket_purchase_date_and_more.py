# Generated by Django 5.0.6 on 2024-12-11 14:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_event_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='purchase_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ticket',
            name='meal_option',
            field=models.CharField(choices=[('none', 'No meal'), ('vegetarian', 'Vegetarian'), ('non_vegetarian', 'Non-vegetarian'), ('vegan', 'Vegan')], default='none', max_length=20),
        ),
    ]
