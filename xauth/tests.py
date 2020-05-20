from datetime import timedelta

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from xauth.models import User
from xauth.utils.token import *


class UserTestCase(APITestCase):
    def test_get_full_name_returns_username_if_neither_names_are_provided(self):
        """
        Return username if it's provided and neither types of names are provided
        """
        user = User(username='username')
        self.assertEqual(user.get_full_name(), user.username)

    def test_get_full_name_returns_names_in_expected_order(self):
        """
        Expected order {surname} {first-name} {last-name}
        """
        s_name, f_name, l_name = ('Sur', 'First', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_full_name(), f'{s_name} {f_name} {l_name}')

    def test_get_full_name_returns_names_with_first_character_of_every_name_capitalized(self):
        s_name, f_name, l_name = ('Sur', 'first', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_full_name(), f'{s_name} First {l_name}')

    def test_get_full_name_returns_removes_any_spaces_at_the_start_or_end_of_every_name(self):
        s_name, f_name, l_name = ('Sur ', ' first', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_full_name(), f'Sur First {l_name}')

    def test_get_short_name_returns_first_word_in_get_full_name(self):
        s_name, f_name, l_name = ('Sur', 'first', 'Last',)
        user = User(username='username', first_name=f_name, last_name=l_name, surname=s_name)
        self.assertEqual(user.get_short_name(), s_name)

    def test_get_short_name_returns_username_if_no_name_is_provided(self):
        user = User(username='username', )
        self.assertEqual(user.get_short_name(), user.username)

    def test_get_full_name_returns_None_if_neither_names_nor_username_is_provided(self):
        user = User()
        self.assertIsNone(user.get_full_name())

    def test_get_short_name_returns_None_if_neither_names_nor_username_is_provided(self):
        user = User()
        self.assertIsNone(user.get_short_name())

    def test_creating_user_without_username_uses_email_as_username(self):
        email = 'user@mail-domain.com'
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.username, email)

    def test_creating_user_with_username_does_not_use_email(self):
        email = 'user@mail-domain.com'
        username = 'user1'
        user = get_user_model().objects.create_user(email=email, username=username)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)

    def test_creating_user_without_manager_methods_works(self):
        """
        Creating user with Django's .create method works same as Managers.create_user
        """
        email = 'user@mail-domain.com'
        user = get_user_model().objects.create(email=email)
        user1 = User(email=f'user.{email}')
        user1.save()
        user2 = User.objects.create(email=f'user1.{email}')
        self.assertEqual(user.username, email)
        self.assertEqual(user.email, email)
        self.assertEqual(user1.username, f'user.{email}')
        self.assertEqual(user2.username, f'user1.{email}')
        self.assertIsNotNone(get_user_model().objects.get_by_natural_key(email))

    def test_check_password_for_created_user_returns_True(self):
        password = 'password123!'
        user = get_user_model().objects.create(email='user@mail-domain.com', password=password)
        user1 = User(email='user1@mail-domain.com', password=password)
        user1.save()

        self.assertEqual(user.check_password(password), True)
        self.assertEqual(user1.check_password(password), True)
        # password hash are never the same even when same password was used
        self.assertNotEqual(user.password, user1.password)

    def test_creating_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None)


class TokenTest(APITestCase):

    def test_tokens_contains_encrypted_and_normal_keys(self):
        token = Token(payload=1)
        token_keys = [key for key, _ in token.tokens.items()]
        self.assertIn('encrypted', token_keys)
        self.assertIn('normal', token_keys)

    def test_value_of_tokens_same_as_value_generate_token(self):
        token = Token(payload=1)
        _token = token._generate_token()
        self.assertEqual(token.tokens, _token)

    def test_value_of_tokens_same_as_values_normal_and_encrypted_properties(self):
        token = Token(payload=1)
        self.assertEqual(token.tokens, {
            'normal': token.normal,
            'encrypted': token.encrypted,
        })

    def test_checked_claims_contains_nbf_exp_and_iat_keys(self):
        token = Token(payload=1)
        checked_claims_keys = [key for key, _ in token.checked_claims.items()]
        self.assertIn('nbf', checked_claims_keys)
        self.assertIn('exp', checked_claims_keys)
        self.assertIn('iat', checked_claims_keys)

    def test_claims_contains_checked_claims(self):
        token = Token(payload=1)
        self.assertDictContainsSubset(token.checked_claims, token.claims)

    def test_claims_contains_payload_key(self):
        token = Token(payload=1)
        claims_keys = [key for key, _ in token.claims.items()]
        self.assertIn(token.payload_key, claims_keys)

    def test_checked_claims_nbf_exp_and_iat_have_alternative_values_if_not_provided(self):
        token = Token(payload=1)
        checked_claims = token.checked_claims
        self.assertIsNot(checked_claims.get('nbf', None), None)
        self.assertIsNot(checked_claims.get('exp', None), None)
        self.assertIsNot(checked_claims.get('iat', None), None)

    def test_claims_payload_is_same_as_constructor_provided(self):
        token = Token(payload=1)
        self.assertEqual(token.claims.get(token.payload_key, None), 1)

    def test_provided_expiry_date_seconds_matches_exp_value(self):
        expiry_date = datetime.now() + timedelta(minutes=5)
        token = Token(payload=1, expiry_date=expiry_date)
        self.assertEqual(token.claims.get('exp', 0), int(expiry_date.strftime('%s')))

    def test_provided_activation_date_seconds_matches_nbf_value(self):
        activation_date = datetime.now() + timedelta(minutes=5)
        token = Token(payload=1, activation_date=activation_date)
        self.assertEqual(token.claims.get('nbf', 0), int(activation_date.strftime('%s')))
        self.assertEqual(token.claims.get('exp', 0), int((activation_date + timedelta(days=60)).strftime('%s')))

    def test_checked_claims_throws_assertion_error_if_activation_date_is_greater_than_expiration_date(self):
        # TODO: Test exception thrown...
        activation_date = datetime.now() + timedelta(days=5)
        expiry_date = datetime.now() + timedelta(minutes=5)
        token = Token(payload=1, activation_date=activation_date, expiry_date=expiry_date)
        # self.assertRaises(AssertionError, token.checked_claims)
        self.assertRaisesMessage(AssertionError, 'Expiration date must be a date later than activation date')

    def test_get_payload_value_without_token_param_same_as_payload(self):
        token = Token(payload=1)
        token._generate_token()
        self.assertEqual(token.get_payload(), 1)
        self.assertEqual(token.get_payload(), token.payload)

    def test_get_payload_value_without_token_param_same_as_payload_with_hs256_algorithm(self):
        token = Token(payload=1, signing_algorithm='HS256')
        token._generate_token()
        self.assertEqual(token.get_payload(), 1)
        self.assertEqual(token.get_payload(), token.payload)
