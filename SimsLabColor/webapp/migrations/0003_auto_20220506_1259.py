# Generated by Django 3.2.12 on 2022-05-06 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0002_auto_20220506_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='img_one_table',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='1_Sharp_Egde/'),
        ),
        migrations.AlterField(
            model_name='img_one_table',
            name='img_label',
            field=models.TextField(blank=True, null=True),
        ),
    ]
