# Generated by Django 3.2.12 on 2022-05-15 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0011_add_img_table_img_desc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='add_img_table',
            name='img_desc',
        ),
    ]
