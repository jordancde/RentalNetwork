from django.db import models
from django.contrib.auth.models import User as User
from jsonfield import JSONField
from django.core.validators import validate_comma_separated_integer_list

class Event(models.Model):
    

    start = models.DateTimeField(auto_now=False, auto_now_add=False)
    end = models.DateTimeField(auto_now=False, auto_now_add=False)

    units = models.IntegerField(default=0)

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
    requests = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=True)

class Listing(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    #active = models.BooleanField()
    events = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=False,default="")
    landlord = models.ForeignKey(
        'Landlord',
        on_delete=models.CASCADE,
    )

class Renter(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    address = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=False,default="Toronto")
    events = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=True)
    requests = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=True)

class Landlord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    listings = models.CharField(validators=[validate_comma_separated_integer_list],max_length=1000,null=False,default="")

class Request(models.Model):
    date = models.DateTimeField(auto_now=True)

    renter = models.ForeignKey(
        'Renter',
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
    )

    accepted = models.BooleanField(default=False)
