from django.db import models
from django.contrib.auth.models import User


class RentalUser(models.Model):

    TYPE_CHOICES = (
        ('L', 'Lanlord'),
        ('R', 'Renter'),
    )
    username = models.CharField(max_length=1, choices=TYPE_CHOICES, primary_key=True)
    user_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
