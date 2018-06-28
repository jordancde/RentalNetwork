from django.contrib.auth.models import User, Group
from rental.models import Renter, Landlord, Event, Listing
from rest_framework import serializers
from oauth2_provider.models import AccessToken

# first we define the serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', "first_name", "last_name", "date_joined")

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name")


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ('name', 'location','description','events','landlord','address')

class RenterEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('start', 'end','address')

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('start', 'end','landlord','renter','units')

class RenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Renter
        fields = ('user', 'events')

class LandlordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landlord
        fields = ('user', 'listings')
