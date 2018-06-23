from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rentalapp.serializers import UserSerializer, GroupSerializer, RentalUserSerializer
from rentalapp.models import RentalUser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope, IsAuthenticatedOrTokenHasScope
from oauth2_provider.views.generic import ScopedProtectedResourceView, ProtectedResourceView
from oauth2_provider.decorators import protected_resource

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from rest_framework import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# Create the API views
class UserList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer



@protected_resource(scopes=['user'])
@api_view(['GET'])
def UserDetail(request):
    if request.method == 'GET':
        user = request.user
        userdata = UserSerializer(user).data
        rentalserializer = RentalUserSerializer(RentalUser.objects.get(pk=user.username))
        userdata["user_type"] = rentalserializer.data["user_type"]
        return Response(userdata)

