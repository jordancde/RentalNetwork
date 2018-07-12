from django.test import TestCase
from oauth2_provider.models import get_access_token_model, get_application_model
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from oauth2_provider.settings import oauth2_settings
from rental.models import Landlord, Renter, Listing, Event, Request
from django.urls import reverse
from rest_framework import status

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()
# Create your tests here.
class BaseTest(TestCase):
    def setUp(self):

        oauth2_settings._SCOPES = ["user"]

        self.renter_user = UserModel.objects.create_user("renter_user", "renter_user@example.com", "123456")
        self.landlord_user = UserModel.objects.create_user("landlord_user", "landlord_user@example.com", "123456")

        self.application = Application.objects.create(
            name="Test Application",
            redirect_uris="http://localhost http://example.com http://example.org",
            user=self.renter_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

        self.renter_access_token = AccessToken.objects.create(
            user=self.renter_user,
            scope="user",
            expires=timezone.now() + timedelta(seconds=300),
            token="secret-access-token-key-renter",
            application=self.application
        )
        self.landlord_access_token = AccessToken.objects.create(
            user=self.landlord_user,
            scope="user",
            expires=timezone.now() + timedelta(seconds=300),
            token="secret-access-token-key-landlord",
            application=self.application
        )

        self.renter_auth = "Bearer {0}".format(self.renter_access_token.token)
        self.landlord_auth = "Bearer {0}".format(self.landlord_access_token.token)
        
        self.client = APIClient()

        self.renter_data = {
            'user': self.renter_user.id,
            'address':"New York"
        }
        self.landlord_data = {
            'user': self.landlord_user.id,
        }

        self.renter_response = self.client.post(
            reverse("renter-list"), 
            self.renter_data,
            format="json",
            HTTP_AUTHORIZATION=self.renter_auth
        )
        self.landlord_response = self.client.post(
            reverse("landlord-list"), 
            self.landlord_data,
            format="json",
            HTTP_AUTHORIZATION=self.landlord_auth
        )

        self.renter=Renter.objects.get(user=self.renter_response.data["user"])
        self.landlord=Landlord.objects.get(user=self.landlord_response.data["user"])


        self.listing_one_data = {
            'name':'walk-in',
            'description':'best place ever',
            'address':"New York"
        }
        self.listing_one_response = self.client.post(
            reverse("listing-list"), 
            self.listing_one_data,
            format="json",
            HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.listing_one = Listing.objects.get(id=self.listing_one_response.data["id"])
        self.landlord=Landlord.objects.get(user=self.landlord_response.data["user"])
        
        self.event_one_data = {
            'start':'2018-07-24T12:45:00Z',
            'end':'2018-07-24T12:45:00Z',
            'listingID':"1",
            'units':"1"
        }
        self.event_one_response = self.client.post(
            reverse("event-list"), 
            self.event_one_data,
            format="json",
            HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.event_one = Event.objects.get(id=self.event_one_response.data["id"])

        self.request_one_data = {
            'eventID':'1'
        }
        self.request_one_response = self.client.post(
            reverse("request-list"), 
            self.request_one_data,
            format="json",
            HTTP_AUTHORIZATION=self.renter_auth
        )
        self.request_one = Request.objects.get(id=self.request_one_response.data["id"])

    
    def test_api_can_create_renter(self):
        self.assertEqual(self.renter_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.renter.user, self.renter_user)
        self.assertEqual(Renter.objects.count(), 1)
    
    def test_api_can_create_landlord(self):
        self.assertEqual(self.landlord_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.landlord.user, self.landlord_user)
        self.assertEqual(Landlord.objects.count(), 1)

    def test_api_can_get_landlord(self):
        response = self.client.get(
            reverse("landlord-detail",kwargs={'pk': self.landlord.user.id}), format="json",HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.landlord.user.id, response.data["user"])
    
    def test_api_can_get_landlord_list(self):
        response = self.client.get(reverse("landlord-list"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.landlord.user.id, response.data[0]["user"])

    def test_api_can_get_renter(self):
        response = self.client.get(
            reverse("renter-detail",kwargs={'pk': self.renter.user.id}), format="json",HTTP_AUTHORIZATION=self.renter_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.renter.user.id, response.data["user"])

    def test_api_can_get_renter_list(self):
        response = self.client.get(reverse("renter-list"),HTTP_AUTHORIZATION=self.renter_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.renter.user.id, response.data[0]["user"])

    # pulls landlord's events
    def test_api_can_get_events_landlord(self):
        response = self.client.get(reverse("event-list"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.event_one.id, response.data[0]["id"])

    # pulls landlord's events
    def test_api_can_get_no_events_renter(self):
        response = self.client.get(reverse("event-list"),HTTP_AUTHORIZATION=self.renter_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_api_can_create_event(self):
        self.assertEqual(self.event_one_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.event_one.id,1)

    def test_api_can_get_event(self):
        response = self.client.get(
            reverse("event-detail",kwargs={'pk': self.event_one.id}), format="json",HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.event_one.id, response.data["id"])
        self.assertEqual(self.event_one.landlord.user.id, response.data["landlord"])
        self.assertEqual(self.event_one_data["units"], str(response.data["units"]))

    def test_api_can_get_listings_renter(self):
        response = self.client.get(reverse("listing-list"),HTTP_AUTHORIZATION=self.renter_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.listing_one.id, response.data[0]["id"])

    def test_api_can_get_listings_landlord(self):  
        response = self.client.get(reverse("listing-list"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(self.listing_one.id, response.data[0]["id"])


    def test_api_can_create_listing_landlord(self):  
        self.assertEqual(self.listing_one_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.listing_one.id,1)

    # TODO: Have to create for custom scopes for listing details
    def test_api_can_get_listing(self):
        response = self.client.get(
            reverse("listing-detail",kwargs={'pk': self.listing_one.id}), format="json",HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.listing_one.id, response.data["id"])
        self.assertEqual(self.listing_one.landlord.user.id, response.data["landlord"])

    def test_api_can_create_request_renter(self):
        self.assertEqual(self.request_one_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.request_one.id,1)

    def test_api_can_get_requests_list_landlord(self):
        response = self.client.get(reverse("request-list"),HTTP_AUTHORIZATION=self.renter_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(self.renter.user.id, response.data[0]["renter"])
        self.assertEqual(self.event_one.id, response.data[0]["event"])
        self.assertEqual(self.event_one.id, response.data[0]["id"])
        self.assertTrue(not response.data[0]["accepted"])

    def test_api_can_get_requests_list_renter(self):
        response = self.client.get(reverse("request-list"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        self.assertEqual(self.renter.user.id, response.data[0]["renter"])
        self.assertEqual(self.event_one.id, response.data[0]["event"])
        self.assertEqual(self.event_one.id, response.data[0]["id"])
        self.assertTrue(not response.data[0]["accepted"])

    def test_api_can_accept_request_landlord(self):
        response = self.client.post(
            reverse("request-list"),data={
                "requestID" : self.request_one.id,
                "accepted": True
            }, format="json",HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request_one = Request.objects.get(id=self.request_one_response.data["id"])
        self.assertTrue(self.request_one.accepted)

    def test_api_can_get_open_requests_landlord(self):
        response = self.client.get(reverse("open-requests"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        self.assertEqual(self.renter.user.id, response.data[0]["renter"])
        self.assertEqual(self.event_one.id, response.data[0]["event"])
        self.assertEqual(self.event_one.id, response.data[0]["id"])
        self.assertTrue(not response.data[0]["accepted"])

    def test_api_can_get_accepted_requests_landlord(self):
        response = self.client.get(reverse("accepted-requests"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        self.test_api_can_accept_request_landlord()

        response = self.client.get(reverse("accepted-requests"),HTTP_AUTHORIZATION=self.landlord_auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(self.renter.user.id, response.data[0]["renter"])
        self.assertEqual(self.event_one.id, response.data[0]["event"])
        self.assertEqual(self.event_one.id, response.data[0]["id"])
        self.assertTrue(response.data[0]["accepted"])

    # TODO: Have to create for custom scopes for request details
    def test_api_can_get_request_details(self):
        response = self.client.get(
            reverse("request-detail",kwargs={'pk': self.request_one.id}), format="json",HTTP_AUTHORIZATION=self.landlord_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.renter.user.id, response.data["renter"])
        self.assertEqual(self.event_one.id, response.data["event"])
        self.assertEqual(self.event_one.id, response.data["id"])
        self.assertTrue(not response.data["accepted"])

    
