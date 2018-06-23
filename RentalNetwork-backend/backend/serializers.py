from django.contrib.auth.models import User, Group
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

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessToken
        fields = ("token", "expires","scope")

