from rest_framework.test import APITestCase
from accounts.models import UserAccounts
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token


class AccountsTest(APITestCase):
    def setUp(self):
        self.test_user1 = UserAccounts.objects.create_user("test_user1", "user@test.com", "testpassword")
        self.registration_url = reverse("account-registration")
        self.get_token_url = reverse("get-token")

    def test_create_user(self):
        input_data = {
            "username": "test_user2",
            "email": "user2@test.com",
            "password": "testpassword"
        }
        response = self.client.post(self.registration_url, input_data, follow='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserAccounts.objects.count(), 2)
        self.assertEqual(response.data["username"], input_data["username"])
        self.assertEqual(response.data["email"], input_data["email"])
        self.assertEqual(response.data["score"], 0)
        self.assertTrue(len(Token.objects.get(user_id=response.data["id"]).key) > 0)

    def test_same_user_name(self):
        input_data = {
            "username": "test_user1",
            "email": "user2@test.com",
            "password": "testpassword"
        }
        response = self.client.post(self.registration_url, input_data, follow='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserAccounts.objects.count(), 1)

    def test_same_email(self):
        input_data = {
            "username": "test_user3",
            "email": "user@test.com",
            "password": "testpassword"
        }
        response = self.client.post(self.registration_url, input_data, follow='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserAccounts.objects.count(), 1)

    def test_no_password(self):
        input_data = {
            "username": "test_user3",
            "email": "use3r@test.com",
            "password": ""
        }
        response = self.client.post(self.registration_url, input_data, follow='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserAccounts.objects.count(), 1)

    def test_short_password(self):
        input_data = {
            "username": "test_user3",
            "email": "use3r@test.com",
            "password": "a"
        }
        response = self.client.post(self.registration_url, input_data, follow='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserAccounts.objects.count(), 1)

    def test_token_creation(self):
        input_data = {
            "username": "test_user2",
            "email": "user2@test.com",
            "password": "testpassword"
        }
        self.client.post(self.registration_url, input_data, follow='json')
        self.client.login(username="test_user2", password='testpassword')
        response = self.client.get(self.get_token_url, follow='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["token"])
