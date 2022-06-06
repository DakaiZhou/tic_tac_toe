# Generated by Django 3.2.13 on 2022-06-06 11:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0005_auto_20220605_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='first_move',
        ),
        migrations.AddField(
            model_name='game',
            name='last_play',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_play', to=settings.AUTH_USER_MODEL),
        ),
    ]
