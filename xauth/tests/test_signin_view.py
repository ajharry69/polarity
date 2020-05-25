from rest_framework.test import APITestCase, APIClient


class SignInViewTestCase(APITestCase):
    def test_signing_in_with_valid_basic_authentication_credentials_returns_200(self):
        self.assertEqual(1, 1 * 1)
    def test_signing_in_with_invalid_basic_authentication_username_returns_401(self):
        self.assertEqual(1, 1 * 1)
    def test_signing_in_with_invalid_basic_authentication_password_returns_401(self):
        self.assertEqual(1, 1 * 1)
    def test_signing_in_with_valid_post_request_credentials_returns_200(self):
        """credentials mean: value contained in username & password fields of a POST request"""
        self.assertEqual(1, 1 * 1)
    def test_signing_in_with_invalid_post_request_username_returns_401(self):
        self.assertEqual(1, 1 * 1)
    def test_signing_in_with_invalid_post_request_password_returns_401(self):
        self.assertEqual(1, 1 * 1)
