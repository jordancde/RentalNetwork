from django.test import TestCase
from oauth2_provider.models import get_access_token_model, get_application_model
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from oauth2_provider.settings import oauth2_settings
from rental.models import Landlord, Renter
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

        # Create 3 listings

    
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
        self.assertEqual(self.landlord.user.id, response.data["user"])

    def test_api_can_get_renter(self):
        response = self.client.get(
            reverse("renter-detail",kwargs={'pk': self.renter.user.id}), format="json",HTTP_AUTHORIZATION=self.renter_auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.renter.user.id, response.data["user"])

    # from stories
    
