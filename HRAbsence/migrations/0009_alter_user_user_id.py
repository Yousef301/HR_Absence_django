# Generated by Django 4.2.7 on 2023-11-12 10:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("HRAbsence", "0008_alter_user_options_remove_user_is_admin_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="user_id",
            field=models.IntegerField(null=True, unique=True, verbose_name="user id"),
        ),
    ]
