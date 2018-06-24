from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
from django.core.validators import validate_comma_separated_integer_list

class Event(models.Model):
    

    start = models.DateTimeField(auto_now=False, auto_now_add=False)
    end = models.DateTimeField(auto_now=False, auto_now_add=False)

    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
    )
    landlord = models.ForeignKey(
        'Landlord',
        on_delete=models.CASCADE,
    )
    renter = models.ForeignKey(
        'Renter',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

class Listing(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    #active = models.BooleanField()

    events = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=True)
    landlord = models.ForeignKey(
        'Landlord',
        on_delete=models.CASCADE,
    )


class Renter(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    events = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=True)

class Landlord(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    listings = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=True)