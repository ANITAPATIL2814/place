# Generated by Django 4.2.16 on 2025-01-16 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('placement', '0008_alter_student_guardian_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='phone',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='phone',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
