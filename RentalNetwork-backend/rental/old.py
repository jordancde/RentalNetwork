from django.test import TestCase
from django.contrib.auth.models import User, Group
from registry.models import Asset, Owner, TransferTransaction, Permission
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import force_authenticate
from registry import views
from oauth2_provider.settings import oauth2_settings
from datetime import datetime, timedelta
from oauth2_provider.models import get_access_token_model, get_application_model
from django.contrib.auth import get_user_model
from django.utils import timezone

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()

ENABLE_COMPOSER_TESTING = False

class CreateOwnerTest(TestCase):
    """This class defines the test suite for the owner model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.email = "<enter email>"
        self.first_name = "<first name>"
        self.last_name = "<last name>"
        self.owner = Owner(
            email=self.email, first_name=self.first_name, last_name=self.last_name)

    def test_model_can_create_an_owner(self):
        """Test the owner model can create a participant."""
        old_count = Owner.objects.count()
        self.owner.save()
        new_count = Owner.objects.count()
        self.assertNotEqual(old_count, new_count)

class CreateAssetTest(TestCase):
    def setUp(self):
        self.owner = Owner(
            email='test@email.com',
            first_name='first name', 
            last_name='last name'
        )
        self.owner.save()

        self.asset = Asset(
            name="test", 
            serial="fff", 
            description="desc",
            owner=self.owner,
        )

    def test_model_can_Create_an_asset(self):
        old_count = Asset.objects.count()
        self.asset.save()
        new_count = Asset.objects.count()
        self.assertNotEqual(old_count, new_count)

class BaseTest(TestCase):
    def setUp(self):
        views.manager.test_mode=not ENABLE_COMPOSER_TESTING

        oauth2_settings._SCOPES = ["user"]

        self.test_user = UserModel.objects.create_user("test_user", "test@example.com", "123456")

        self.application = Application.objects.create(
            name="Test Application",
            redirect_uris="http://localhost http://example.com http://example.org",
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

        self.access_token = AccessToken.objects.create(
            user=self.test_user,
            scope="read write user",
            expires=timezone.now() + timedelta(seconds=300),
            token="secret-access-token-key",
            application=self.application
        )

        self.auth = "Bearer {0}".format(self.access_token.token)
        self.client = APIClient()

        self.owner_one_data = {
            'email': 'test1@email.com',
            'first_name': 'first name', 
            'last_name': 'last name'
        }
        self.owner_one_response = self.client.post(
            reverse("owner_list"), #need to give urls namespace
            self.owner_one_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )

        self.owner_two_data = {
            'email': 'test2@email.com',
            'first_name': 'first name', 
            'last_name': 'last name'
        }
        self.owner_two_response = self.client.post(
            reverse("owner_list"), 
            self.owner_two_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )

        self.owner_one=Owner.objects.get(uuid=self.owner_one_response.data["uuid"])
        self.owner_two=Owner.objects.get(uuid=self.owner_two_response.data["uuid"])

class OwnerViewTestCase(BaseTest):
    """Test suite for the api views."""

    def setUp(self):
        super(OwnerViewTestCase,self).setUp()


    def test_api_can_create_an_owner(self):
        self.assertEqual(self.owner_one.email, self.owner_one_data["email"])
        self.assertEqual(self.owner_one.first_name, self.owner_one_data["first_name"])
        self.assertEqual(self.owner_one.last_name, self.owner_one_data["last_name"])
        self.assertEqual(self.owner_one_response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_schema(self):
        owner_details = {'email': 'test1@email.com','last_name': 4}
        response = self.client.post(reverse("owner_list"),owner_details,HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_an_existing_owner(self):
        # owner email exists
        owner_details = {'email': 'test1@email.com','first_name': 'f','last_name': 'l'}
        response = self.client.post(reverse("owner_list"),owner_details,HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_api_can_get_an_owner(self):
        
        response = self.client.get(
            reverse("owner_details",kwargs={'pk': self.owner_one.uuid}), format="json",HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, self.owner_one.uuid)
        self.assertEqual(response.data["active"], True)
        self.assertEqual(self.owner_one.email, response.data["email"])
        self.assertEqual(self.owner_one.first_name, response.data["first_name"])
        self.assertEqual(self.owner_one.last_name, response.data["last_name"])
        self.assertTrue(response.data["permissions"])

    def test_get_non_existant_owner(self):
        response = self.client.get(
            reverse("owner_details",kwargs={'pk': 4}), format="json",HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_api_can_get_owner_list(self):
        
        response = self.client.get(
            reverse("owner_list"),format="json",HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Owner.objects.all().count())

        self.assertEqual(response.data[0]["active"], True)
        self.assertEqual(self.owner_one.email, response.data[0]["email"])
        self.assertEqual(self.owner_one.first_name, response.data[0]["first_name"])
        self.assertEqual(self.owner_one.last_name, response.data[0]["last_name"])
        self.assertTrue(response.data[0]["permissions"])

    def test_api_can_update_owner(self):

        change_owner = {
            'email': 'new email',
            'first_name': 'new first name', 
            'last_name': 'new last name'
        }
        response = self.client.patch(
            reverse(
                "owner_details",
                kwargs={'pk': self.owner_one.uuid}
            ),
            change_owner,
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.owner_one=Owner.objects.get(uuid=self.owner_one.uuid)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.owner_one.email, change_owner["email"])
        self.assertEqual(self.owner_one.first_name, change_owner["first_name"])
        self.assertEqual(self.owner_one.last_name, change_owner["last_name"])

        self.assertEqual(self.owner_one.email, response.data["email"])
        self.assertEqual(self.owner_one.first_name, response.data["first_name"])
        self.assertEqual(self.owner_one.last_name, response.data["last_name"])

    def test_update_non_existant_owner(self):
        change_owner = {'email': 'new email','first_name': 'new first name', 'last_name': 'new last name'}
        response = self.client.patch(
            reverse(
                "owner_details",
                kwargs={'pk': 4}
            ),
            change_owner,
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_owner_invalid_schema(self):
        change_owner = {'last_name': 4}
        response = self.client.patch(
            reverse(
                "owner_details",
                kwargs={'pk': self.owner_one.uuid}
            ),
            change_owner,
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_can_delete_owner(self):
        response = self.client.delete(
            reverse(
                "owner_details",
                kwargs={'pk': self.owner_one.uuid}
            ),
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Owner.objects.filter(uuid=self.owner_one.uuid).count(), 0)
    
    def test_api_delete_non_existant_owner(self):
        response = self.client.delete(
            reverse(
                "owner_details",
                kwargs={'pk': 4}
            ),
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    

class AssetViewTestCase(BaseTest):
    def setUp(self):
        super(AssetViewTestCase,self).setUp()
        self.asset_data = {
            "name":"test", 
            "serial":"fff", 
            "description":"desc",
            "original_owner_email":self.owner_one.email,
            "current_owner_email":self.owner_one.email,
        }

        self.asset_response = self.client.post(
            reverse("asset_list"), #need to give urls namespace
            self.asset_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )

        self.asset=Asset.objects.get(uuid=self.asset_response.data["uuid"])

    def test_api_can_create_an_asset(self):
        self.assertEqual(self.asset_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.asset.name, self.asset_data["name"])
        self.assertEqual(self.asset.serial, self.asset_data["serial"])
        self.assertEqual(self.asset.description, self.asset_data["description"])
        self.assertEqual(self.owner_one.uuid, self.asset.owner.uuid)
        self.assertTrue(self.asset.date_created)
        self.assertTrue(self.asset.last_transaction)

    def test_create_asset_invalid_schema(self):
        asset_details = {'email': 'test1@email.com'}
        response = self.client.post(reverse("asset_list"),asset_details,HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_asset_existing_serial(self):
        asset_data = {
            "name":"test", 
            "serial":"fff", 
            "description":"desc",
            "original_owner_email":self.owner_one.email,
            "current_owner_email":self.owner_one.email,
        }
        response = self.client.post(reverse("asset_list"),asset_data,HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_asset_bad_owner(self):
        asset_data = {
            "name":"test", 
            "serial":"fff", 
            "description":"desc",
            "original_owner_email":"hi@email.com",
            "current_owner_email":"hi@email.com"
        }
        response = self.client.post(reverse("asset_list"),asset_data,HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_api_can_get_an_asset(self):
        response = self.client.get(
            reverse(
                "asset_details",
                kwargs={'pk': self.asset.uuid}
            ), 
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.asset.name, response.data["name"])
        self.assertEqual(self.asset.serial, response.data["serial"])
        self.assertEqual(self.asset.description, response.data["description"])
        self.assertEqual(str(self.asset.uuid), response.data["uuid"])
        self.assertEqual(self.owner_one.uuid,response.data["owner"])
        self.assertTrue(response.data["date_created"])
        self.assertTrue(response.data["last_transaction"])

    def test_get_non_existant_asset(self):
        response = self.client.get(
            reverse("asset_details",kwargs={'pk': 4}), format="json",HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_api_can_get_asset_list(self):
        response = self.client.get(
            reverse(
                "asset_list"
            ), 
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Asset.objects.all().count())

        self.assertEqual(self.asset.name, response.data[0]["name"])
        self.assertEqual(self.asset.serial, response.data[0]["serial"])
        self.assertEqual(self.asset.description, response.data[0]["description"])
        self.assertEqual(str(self.asset.uuid), response.data[0]["uuid"])
        self.assertEqual(self.owner_one.uuid,response.data[0]["owner"])
        self.assertTrue(response.data[0]["date_created"])
        self.assertTrue(response.data[0]["last_transaction"])

    def test_api_can_update_asset(self):
        change_asset = {
            'name': 'new asset name',
            'serial': 'new asset serial id', 
            'description': 'new disc'
        }
        response = self.client.patch(
            reverse(
                "asset_details",  # url namespace
                kwargs={'pk': self.asset.uuid}
            ),
            change_asset,
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset=Asset.objects.get(uuid=self.asset_response.data["uuid"])

        self.assertEqual(self.asset.name, change_asset["name"])
        self.assertEqual(self.asset.serial, change_asset["serial"])
        self.assertEqual(self.asset.description, change_asset["description"])

        self.assertEqual(self.asset.name, response.data["name"])
        self.assertEqual(self.asset.serial, response.data["serial"])
        self.assertEqual(self.asset.description, response.data["description"])

        self.assertEqual(self.owner_one.uuid,response.data["owner"])
        self.assertTrue(response.data["date_created"])
        self.assertTrue(response.data["last_transaction"])
        self.assertEqual(str(self.asset.uuid),response.data["uuid"])

    def test_update_non_existant_asset(self):
        change_asset = {'name': 'new name'}
        response = self.client.patch(
            reverse(
                "asset_details",
                kwargs={'pk': 4}
            ),
            change_asset,
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_asset_invalid_schema(self):
        change_asset = {'name': 4}
        response = self.client.patch(
            reverse(
                "asset_details",
                kwargs={'pk': self.asset.uuid}
            ),
            change_asset,
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_can_delete_asset(self):
        response = self.client.delete(
            reverse(
                "asset_details",  # url namespace
                kwargs={'pk': self.asset.uuid}
            ),
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.filter(uuid=self.asset.uuid).count(), 0)

    def test_api_delete_non_existant_asset(self):
        response = self.client.delete(
            reverse(
                "asset_details",
                kwargs={'pk': 4}
            ),
            format='json',
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PermissionsTest(BaseTest):
    def setUp(self):
        super(PermissionsTest,self).setUp()
        self.permission = Permission.objects.get(id=self.owner_one.permissions)

    def test_api_owner_transfer_permission_created(self):
        response = self.client.get(
            reverse(
                "permission_details",
                kwargs={'pk': self.owner_one.permissions}
            ), 
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.owner_one.permissions, str(response.data["id"]))
        self.assertEqual("can_transfer", response.data["name"])
        self.assertEqual(self.owner_one.uuid, response.data["owner"])
        self.assertEqual(True, response.data["status"])
        self.assertTrue(response.data["edit_date"])

    def test_api_can_get_permission_list(self):
        response = self.client.get(
            reverse(
                "permission_list"
            ), 
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), Permission.objects.all().count())

        self.assertEqual(self.owner_one.permissions, str(response.data[0]["id"]))
        self.assertEqual("can_transfer", response.data[0]["name"])
        self.assertEqual(self.owner_one.uuid, response.data[0]["owner"])
        self.assertEqual(True, response.data[0]["status"])
        self.assertTrue(response.data[0]["edit_date"])

    def test_api_create_new_permission(self):
        self.permission_data = {
            'email': self.owner_one_data["email"],
            'name': 'test',
            'status': True
        }
        response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.owner_one=Owner.objects.get(uuid=self.owner_one.uuid)
        self.permission = Permission.objects.get(id=response.data["id"])

        self.assertEqual(self.permission.name, self.permission_data["name"])
        self.assertEqual(self.permission.owner.email, self.permission_data["email"])
        self.assertEqual(self.permission.status, self.permission_data["status"])

        self.assertEqual(self.permission.id, response.data["id"])
        self.assertEqual(self.permission.name, response.data["name"])
        self.assertEqual(self.permission.owner.uuid, response.data["owner"])
        self.assertEqual(self.permission.status, response.data["status"])
        self.assertTrue(response.data["edit_date"])

        self.assertIn(str(response.data["id"]),self.owner_one.permissions.split(','))

    def test_api_create_permission_invalid_email(self):
        self.permission_data = {
            'email': "hi@email.com",
            'name': 'test',
            'status': True
        }
        response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_create_permission_invalid_schema(self):
        self.permission_data = {
            'name': 'test',
            'status': True
        }
        response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_update_transfer_permission(self):
        self.permission_data = {
            'email': self.owner_one.email,
            'name': self.permission.name,
            'status': False
        }
        response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner= Owner.objects.get(uuid=self.owner_one.uuid)
        self.permission = Permission.objects.get(id=response.data["id"])

        self.assertEqual(self.permission.name, self.permission_data["name"])
        self.assertEqual(self.permission.owner.email, self.permission_data["email"])
        self.assertEqual(self.permission.status, self.permission_data["status"])

        self.assertEqual(self.permission.id, response.data["id"])
        self.assertEqual(self.permission.name, response.data["name"])
        self.assertEqual(self.permission.owner.uuid, response.data["owner"])
        self.assertEqual(self.permission.status, response.data["status"])
        self.assertTrue(response.data["edit_date"])

        self.assertIn(str(response.data["id"]),self.owner_one.permissions.split(','))

    def test_api_update_invalid_owner(self):
        self.permission_data = {
            'email': 'hi@email.com',
            'name': self.permission.name,
            'status': False
        }
        response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_update_invalid_schema(self):
        self.permission_data = {
            'email': 'hi@email.com',
            'name': 3,
            'status': False
        }
        response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TransferTest(AssetViewTestCase):
    def setUp(self):
        super(TransferTest,self).setUp()
        self.permission = Permission.objects.get(id=self.owner_one.permissions)
        
    def test_api_can_transfer(self):
        self.transfer_data = {
            'email': self.owner_two.email,
            'uuid': self.asset.uuid,
        }
        transfer_response = self.client.post(
            reverse("transfer_list"), #need to give urls namespace
            self.transfer_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        
        self.assertEqual(transfer_response.status_code, status.HTTP_201_CREATED)
        self.asset=Asset.objects.get(uuid=self.asset.uuid)

        self.transfer=TransferTransaction.objects.get(id=transfer_response.data["id"])
        
        # Ownership transfer
        self.assertEqual(self.asset.owner.uuid, self.owner_two.uuid)

        # Transfer Response matches expected output
        self.assertTrue(transfer_response.data["id"])
        self.assertTrue(transfer_response.data["date"])
        self.assertEqual(transfer_response.data["asset"], str(self.asset.uuid))
        self.assertEqual(transfer_response.data["previous_owner"], str(self.owner_one.uuid))
        self.assertEqual(transfer_response.data["new_owner"], str(self.owner_two.uuid))

        # Transfer object matches response
        self.assertTrue(transfer_response.data["id"],self.transfer.id)
        self.assertTrue(transfer_response.data["date"],self.transfer.date)
        self.assertEqual(transfer_response.data["asset"], self.transfer.asset)
        self.assertEqual(transfer_response.data["previous_owner"], self.transfer.previous_owner)
        self.assertEqual(transfer_response.data["new_owner"], self.transfer.new_owner)

    def test_api_transfer_invalid_owner(self):
        self.transfer_data = {
            'email': "hi@hi.comself.owner_two.email",
            'uuid': self.asset.uuid,
        }
        response = self.client.post(
            reverse("transfer_list"), #need to give urls namespace
            self.transfer_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_transfer_invalid_asset(self):
        self.transfer_data = {
            'email': self.owner_two.email,
            'uuid': 4,
        }
        response = self.client.post(
            reverse("transfer_list"), #need to give urls namespace
            self.transfer_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_api_can_get_a_transfer(self):
        self.test_api_can_transfer()
        response = self.client.get(
            reverse(
                "transfer_details",
                kwargs={'pk': self.transfer.id}
            ), 
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data["id"],self.transfer.id)
        self.assertTrue(response.data["date"],self.transfer.date)
        self.assertEqual(response.data["asset"], self.transfer.asset)
        self.assertEqual(response.data["previous_owner"], self.transfer.previous_owner)
        self.assertEqual(response.data["new_owner"], self.transfer.new_owner)
        
    def test_api_can_get_transfer_list(self):
        self.test_api_can_transfer()
        response = self.client.get(
            reverse(
                "transfer_list"
            ), 
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), TransferTransaction.objects.all().count())

        self.assertTrue(response.data[0]["id"],self.transfer.id)
        self.assertTrue(response.data[0]["date"],self.transfer.date)
        self.assertEqual(response.data[0]["asset"], self.transfer.asset)
        self.assertEqual(response.data[0]["previous_owner"], self.transfer.previous_owner)
        self.assertEqual(response.data[0]["new_owner"], self.transfer.new_owner)

    def test_api_transfer_with_self(self):
        
        self.transfer_data = {
            'email': self.owner_one.email,
            'uuid': self.asset.uuid,
        }
        response = self.client.post(
            reverse("transfer_list"), #need to give urls namespace
            self.transfer_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_api_transfer_without_permission(self):
        
        self.permission_data = {
            'email': self.owner_one.email,
            'name': self.permission.name,
            'status': False
        }
        permission_response = self.client.post(
            reverse("permission_list"), #need to give urls namespace
            self.permission_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )

        self.transfer_data = {
            'email': self.owner_two.email,
            'uuid': self.asset.uuid,
        }
        transfer_response = self.client.post(
            reverse("transfer_list"), #need to give urls namespace
            self.transfer_data,
            format="json",
            HTTP_AUTHORIZATION=self.auth
        )
 
        self.assertEqual(transfer_response.status_code, status.HTTP_400_BAD_REQUEST)

