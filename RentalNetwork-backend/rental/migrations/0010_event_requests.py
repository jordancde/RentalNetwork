# Generated by Django 2.0.6 on 2018-07-02 17:31

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0009_request_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='requests',
            field=models.CharField(max_length=1000, null=True, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
    ]
