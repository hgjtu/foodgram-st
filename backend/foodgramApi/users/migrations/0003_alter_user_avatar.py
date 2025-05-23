# Generated by Django 5.2.1 on 2025-05-08 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="static/media/userpic-icon.jpg",
                null=True,
                upload_to="users/avatars/",
                verbose_name="Аватар",
            ),
        ),
    ]
