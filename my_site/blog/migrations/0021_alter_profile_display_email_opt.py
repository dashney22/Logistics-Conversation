# Generated by Django 3.2.8 on 2023-02-14 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_profile_display_email_opt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='display_email_opt',
            field=models.BooleanField(default=False),
        ),
    ]
