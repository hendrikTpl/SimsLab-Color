# Generated by Django 3.2.12 on 2022-05-15 16:16

from django.db import migrations, models
import webapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0009_auto_20220513_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_img_table',
            name='img_file',
            field=models.ImageField(upload_to=webapp.models.img_path),
        ),
    ]
