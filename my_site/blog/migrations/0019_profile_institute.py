# Generated by Django 3.2.8 on 2023-02-13 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0018_auto_20230213_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='institute',
            field=models.CharField(default='Unknown Institute', max_length=100),
        ),
    ]