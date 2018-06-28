from django.shortcuts import render
from django.contrib.auth.models import User, Group

from rental.serializers import UserSerializer, GroupSerializer,ListingSerializer, EventSerializer
from rental.models import Landlord, Event, Listing

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
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['user']
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    required_scopes = ['user']
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class EventDetails(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['user']
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ListingDetails(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['user']
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

@protected_resource(scopes=['user'])
@api_view(['GET','POST'])
def Events(request):
    if request.method == 'GET':
        user = request.user
        landlord = Landlord.objects.get(pk=user.id)
        listings = landlord.listings.split(',')
        if(not listings): return Response("No Listings")

        response = []
        for listing in listings:
            l = Listing.objects.get(pk=listing)
            events = l.events.split(',')
            if not events: continue
            for event in events:
                if not event: continue
                e = Event.objects.get(pk=event)
                response.append(EventSerializer(e).data)
    
        return Response(response)

    if request.method == 'POST':
        data = request.data
        user = request.user

        landlord = Landlord.objects.get(pk=user.id)
        landlordListings = landlord.listings.split(',')

        if(data["listingID"] not in landlordListings):
            return Response("not your listing")

        listing = Listing.objects.get(pk=data["listingID"])

        event = Event.objects.create(
            start=data.get("start"), 
            end=data.get("end"),
            listing=listing,
            landlord=landlord,
            units=data.get("units")
        )
        
        listing.events+=","+str(event.id)
        listing.save()

        return Response("Success")



@protected_resource(scopes=['user'])
@api_view(['Post'])
def FindListingsView(request): 
    pass



