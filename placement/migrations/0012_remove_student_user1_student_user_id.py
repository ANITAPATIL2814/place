# Generated by Django 4.2.16 on 2025-01-08 23:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('placement', '0011_rename_user_student_user1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='user1',
        ),
        migrations.AddField(
            model_name='student',
            name='user_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
