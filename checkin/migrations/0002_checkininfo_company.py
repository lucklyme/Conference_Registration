# Generated by Django 2.0.6 on 2018-07-31 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkininfo',
            name='company',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='所属公司'),
        ),
    ]
