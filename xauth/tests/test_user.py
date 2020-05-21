from django.contrib.auth import get_user_model
from django.utils.datetime_safe import datetime
from rest_framework.test import APITestCase

from xauth.models import User
from xauth.utils import enums


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

    def test_verification_token_expires_after_1_hour_by_default(self):
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        token = user.verification_token
        exp_value = token.claims.get('exp', 0)
        default_activation_date_seconds = int(datetime.now().strftime('%s'))

        self.assertGreaterEqual(exp_value, default_activation_date_seconds)
        self.assertEqual(int((exp_value - default_activation_date_seconds) / (60 * 60)), 1)

    def test_password_reset_token_expires_after_30_minutes_by_default(self):
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        token = user.password_reset_token
        exp_value = token.claims.get('exp', 0)
        default_activation_date_seconds = int(datetime.now().strftime('%s'))

        self.assertGreaterEqual(exp_value, default_activation_date_seconds)
        self.assertEqual(int((exp_value - default_activation_date_seconds) / 60), 30)

    def test_is_verified_for_non_email_provider_or_superuser_and_or_staff_users(self):
        provider = enums.AuthProvider.GOOGLE.name
        user = get_user_model().objects.create(email='user@mail-domain.com', provider=provider)
        user1 = get_user_model().objects.create(email='user1@mail-domain.com', is_superuser=True, password='9V55w0rd')
        user2 = get_user_model().objects.create(email='user2@mail-domain.com', is_staff=True)
        user3 = get_user_model().objects.create(email='user3@mail-domain.com', provider=enums.AuthProvider.EMAIL.name,
                                                is_staff=True)
        user4 = get_user_model().objects.create(email='user4@mail-domain.com', provider=enums.AuthProvider.PHONE.name, )

        self.assertIs(user.is_verified, True)
        self.assertIs(user1.is_verified, True)
        self.assertIs(user2.is_verified, True)
        self.assertIs(user3.is_verified, True)
        self.assertIs(user4.is_verified, False)

    def test_creating_user_account_without_password_returns_empty_or_none_password(self):
        password = ''
        password1 = None
        password2 = 'None'
        user = get_user_model().objects.create_user(email='mitch@mitch.com', username='mitch123', password=password)
        user1 = get_user_model().objects.create_user(email='mitch1@mitch.com', username='mitch1234', password=password1)
        user2 = get_user_model().objects.create_user(email='mitch2@mitch.com', username='mitch12345',
                                                     password=password2)
        self.assertIsNone(user.password)
        self.assertIsNone(user1.password)
        self.assertIs(user2.check_password(raw_password=password2), True)
