from django.shortcuts import render
from django.contrib.auth.models import User, Group

from rental.serializers import UserSerializer, GroupSerializer,ListingSerializer, EventSerializer
from rental.models import Landlord, Event, Listing,Renter

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope, IsAuthenticatedOrTokenHasScope
from oauth2_provider.views.generic import ScopedProtectedResourceView, ProtectedResourceView
from oauth2_provider.decorators import protected_resource
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from rest_framework import serializers
from rental import maps


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

        if(get_user_type(user) is Landlord):

            landlord = Landlord.objects.get(user=user.id)
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
        
        elif(get_user_type(user) is Renter):

            renter = Renter.objects.get(user=user.id)
            if(not renter.events):
                return Response([])

            event_ids = renter.events.split(',')

            events = []
            for id in event_ids:
                events.append(EventSerializer(Event.objects.get(pk=id)).data)

            return Response(events)

        else:
            return Response("Not a landlord",status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        data = request.data
        user = request.user

        if(get_user_type(user) is not Landlord):
            return Response("Not a landlord",status=status.HTTP_403_FORBIDDEN)

        landlord = Landlord.objects.get(pk=user.id)
        landlordListings = landlord.listings.split(',')

        if(data["listingID"] not in landlordListings):
            return Response("not your listing")

        listing = Listing.objects.get(pk=data["listingID"])

        try:
            event = Event.objects.create(
                start=data.get("start"), 
                end=data.get("end"),
                listing=listing,
                landlord=landlord,
                units=data.get("units")
            )
        except:
            return Response("Invalid parameters",status=status.HTTP_400_BAD_REQUEST)
        
        listing.events+=","+str(event.id)
        listing.save()

        return Response(EventSerializer(event).data)

@protected_resource(scopes=['user'])
@api_view(['GET','POST'])
def ListingsView(request): 
    if request.method == 'GET':
        if(get_user_type(request.user)==Renter):
            #for RENTER
            listings = Listing.objects.all()
            renter = Renter.objects.get(pk=request.user.id)

            renter_address = renter.address

            if(not maps.test_address(renter.address)):
                return Response("Invalid Renter Address",status=status.HTTP_400_BAD_REQUEST)

            sorted_listings,listings_to_trips = sort_listings(renter_address,listings)

            response = []

            for listing in sorted_listings:
                data = ListingSerializer(listing).data
                data["distance"] = listings_to_trips[listing].distance
                response.append(data)

            return Response(response)

        elif(get_user_type(request.user)==Landlord):

            user = request.user

            landlord = Landlord.objects.get(pk=user.id)
            landlord_listing_ids = landlord.listings.split(',')

            listings = []
            for id in landlord_listing_ids:
                listings.append(Listing.objects.get(pk=id))
            
            return Response(ListingSerializer(listings,many=True).data)
        
        else:
            return Response("Not landlord or renter",status=status.HTTP_403_FORBIDDEN)
            
    if request.method == 'POST':
        data = request.data
        user = request.user

        if(get_user_type(user) is not Landlord):
            return Response("Not a landlord",status=status.HTTP_403_FORBIDDEN)

        landlord = Landlord.objects.get(pk=user.id)

        if(not maps.test_address(data.get("address"))):
            return Response("Invalid Address",status=status.HTTP_400_BAD_REQUEST)

        try:
            listing = Listing.objects.create(
                name=data.get("name"), 
                description=data.get("description"),
                address=data.get("address"),
                landlord=landlord,
            )
        except:
            return Response("Invalid parameters",status=status.HTTP_400_BAD_REQUEST)
        
        return Response(ListingSerializer(listing).data)

def sort_listings(renter_address,listings):
    sorted_listings = []

    origin = renter_address

    listings_to_trips = maps.get_trips(origin,listings)

    for listing, trip in listings_to_trips.items():
        i = 0
        if(len(sorted_listings) == 0): 
            sorted_listings.append(listing)
            continue

        while(i<len(sorted_listings) and trip.distance>listings_to_trips[sorted_listings[i]].distance):
            i+=1
        sorted_listings.insert(i,listing)

    return sorted_listings, listings_to_trips
        
def get_user_type(user):
    id = user.id

    if(Renter.objects.filter(user=user).count()>0):
        return Renter
    elif(Landlord.objects.filter(user=user).count()>0):
        return Landlord
    elif(User.objects.filter(id=id).count()>0):
        return User
    else:
        return None









    





