# Generated by Django 2.0.6 on 2018-06-30 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0004_auto_20180628_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]