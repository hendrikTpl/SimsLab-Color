# Generated by Django 3.2.12 on 2022-05-15 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_alter_add_img_table_img_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='add_img_table',
            name='img_desc',
            field=models.TextField(blank=True, null=True),
        ),
    ]
