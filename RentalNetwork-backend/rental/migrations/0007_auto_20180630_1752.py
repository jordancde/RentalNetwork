# Generated by Django 2.0.6 on 2018-06-30 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0006_remove_listing_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='location',
            new_name='address',
        ),
    ]
