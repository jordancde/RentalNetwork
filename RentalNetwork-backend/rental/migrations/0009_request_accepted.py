# Generated by Django 2.0.6 on 2018-07-02 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0008_auto_20180702_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]
