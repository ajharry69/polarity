from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.datetime_safe import datetime
from rest_framework.test import APITestCase

from xauth.models import User, Metadata
from xauth.utils import enums
from xauth.utils.settings import DATE_INPUT_FORMAT


def _update_metadata(user, tp_gen_time: timedelta = None, vc_gen_time: timedelta = None):
    meta = Metadata.objects.get_or_create(user=user)[0]
    if tp_gen_time is not None:
        meta.tp_gen_time = timezone.now() + (tp_gen_time if tp_gen_time is not None else timedelta(seconds=0))
    if vc_gen_time is not None:
        meta.vc_gen_time = timezone.now() + (vc_gen_time if vc_gen_time is not None else timedelta(seconds=0))
    meta.save()

    return meta


class UserTestCase(APITestCase):

    def verification_or_reset_succeeded(self, message, token):
        self.assertIsNotNone(token)
        self.assertIsNone(message)
        self.assertEqual(int((token.claims.get('exp', 0) - int(datetime.now().strftime('%s'))) / (60 * 60 * 24)), 60)

    def password_reset_error(self, user, new_password, error_message, correct_password=None, incorrect_password=None):
        if incorrect_password is not None:
            token, message = user.reset_password(
                temporary_password=incorrect_password,
                new_password=new_password,
            )
            self.assertIsNone(token)
            self.assertIsNotNone(message)
            self.assertEqual(message, error_message)
        if correct_password is not None:
            token1, message1 = user.reset_password(
                temporary_password=correct_password,
                new_password=new_password,
            )
            self.assertIsNone(token1)
            self.assertIsNotNone(message1)
            self.assertEqual(message1, error_message)

    def account_verification_error(self, user, error_message, correct_code=None, incorrect_code=None):
        if incorrect_code is not None:
            token, message = user.verify(code=incorrect_code)
            self.assertIsNone(token)
            self.assertIsNotNone(message)
            self.assertEqual(message, error_message)
        if correct_code is not None:
            token1, message1 = user.verify(code=correct_code)
            self.assertIsNone(token1)
            self.assertIsNotNone(message1)
            self.assertEqual(message1, error_message)

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
        self.assertEqual(user.provider, enums.AuthProvider.EMAIL.name)
        self.assertEqual(user.username, email)
        self.assertIsNotNone(user.password)
        self.assertIs(user.has_usable_password(), False)

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
        user = get_user_model().objects.create(email='user@mail-domain.com', )
        user.password = password
        user.save(auto_hash_password=True)
        user1 = User(email='user1@mail-domain.com', password=password)
        user1.save(auto_hash_password=True)

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
        phone_provider = enums.AuthProvider.PHONE.name
        user = get_user_model().objects.create(email='user@mail-domain.com', provider=provider)
        user1 = get_user_model().objects.create(email='user1@mail-domain.com', is_superuser=True, password='9V55w0rd')
        user2 = get_user_model().objects.create(email='user2@mail-domain.com', is_staff=True)
        user3 = get_user_model().objects.create(email='user3@mail-domain.com', provider=enums.AuthProvider.EMAIL.name,
                                                is_staff=True)
        user4 = get_user_model().objects.create(email='user4@mail-domain.com', provider=phone_provider, )

        self.assertEqual(user4.provider, phone_provider)
        self.assertIs(user.is_verified, True)
        self.assertIs(user1.is_verified, True)
        self.assertIs(user2.is_verified, True)
        self.assertIs(user3.is_verified, True)
        self.assertIs(user4.is_verified, False)

    def test_creating_user_account_without_password_returns_empty_or_none_password(self):
        password = ''
        password1 = None
        password2 = 'None'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', password=password)
        user1 = get_user_model().objects.create_user(email='user1@mail-domain.com', username='user1234',
                                                     password=password1)
        user2 = get_user_model().objects.create_user(email='user2@mail-domain.com', username='user12345',
                                                     password=password2)
        self.assertIsNotNone(user.password)
        self.assertIsNotNone(user1.password)
        self.assertIs(user2.check_password(raw_password=password2), True)

    def test_request_password_reset_returns_30minute_valid_token_and_temporary_password(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        token, password = user.request_password_reset(send_mail=False)
        metadata = Metadata.objects.get(pk=user.id)

        self.assertIsNotNone(metadata)
        self.assertIsNotNone(token)
        self.assertIsNotNone(password)
        self.assertEqual(int((token.claims.get('exp', 0) - int(datetime.now().strftime('%s'))) / 60), 30)
        self.assertIs(metadata.check_temporary_password(password), True)

    def test_request_verification_returns_1hour_valid_token_and_verification_code(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        token, code = user.request_verification(send_mail=False)
        metadata = Metadata.objects.get(pk=user.id)

        self.assertIsNotNone(metadata)
        self.assertIsNotNone(token)
        self.assertIsNotNone(code)
        self.assertEqual(int((token.claims.get('exp', 0) - int(datetime.now().strftime('%s'))) / (60 * 60)), 1)
        self.assertIs(metadata.check_verification_code(code), True)

    def test_reset_password_with_expired_password_returns_None_token_and_expired_message(self):
        """
        Returned values are same for a correct or incorrect expired reset password
        """
        new_password = 'Qw3ty12345!@#$%'
        incorrect_password = '1ncorrect'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_password = user.request_password_reset(send_mail=False)

        # adjust temporary password's expiry date
        tp_gen_time = timedelta(minutes=-30, seconds=-1)
        _update_metadata(user, tp_gen_time=tp_gen_time)
        self.password_reset_error(user, new_password, 'expired', correct_password, incorrect_password)

    def test_reset_password_with_incorrect_unexpired_password_returns_None_token_and_incorrect_message(self):
        new_password = 'Qw3ty12345!@#$%'
        incorrect_password = '1ncorrect'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_password = user.request_password_reset(send_mail=False)
        self.password_reset_error(user, new_password, 'incorrect', incorrect_password=incorrect_password)

    def test_reset_password_with_correct_password_returns_Token_expiring_after_60days_and_None_message(self):
        new_password = 'Qw3ty12345!@#$%'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_password = user.request_password_reset(send_mail=False)

        token, message = user.reset_password(
            temporary_password=correct_password,
            new_password=new_password,
        )
        # post-reset
        self.verification_or_reset_succeeded(message, token)
        # make sure users password was not changed in the process
        self.assertIs(user.check_password(new_password), True)

    def test_verify_with_expired_code_returns_None_token_and_expired_message(self):
        """
        Returned values are same for a correct or incorrect expired reset password
        """
        incorrect_code = '123456'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_code = user.request_verification(send_mail=False)

        # adjust temporary password's expiry date
        vc_gen_time = timedelta(hours=-1, seconds=-1)
        _update_metadata(user, vc_gen_time=vc_gen_time)
        self.account_verification_error(user, 'expired', correct_code, incorrect_code)

    def test_verify_with_incorrect_unexpired_code_returns_None_token_and_incorrect_message(self):
        incorrect_code = '123456'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', )
        _, correct_code = user.request_verification(send_mail=False)
        self.account_verification_error(user, 'incorrect', incorrect_code=incorrect_code)

    def test_verify_with_correct_code_returns_Token_expiring_after_60days_and_None_message(self):
        password = 'password'
        user = get_user_model().objects.create_user(email='user@mail-domain.com', username='user123', password=password)
        _, correct_code = user.request_verification(send_mail=False)

        # pre-verification
        self.assertIs(user.is_verified, False)
        self.assertIs(user.check_password(password), True)
        # verification
        token, message = user.verify(code=correct_code)
        # post-verification
        self.verification_or_reset_succeeded(message, token)
        self.assertIs(user.is_verified, True)
        # make sure users password was not changed in the process
        self.assertIs(user.check_password(password), True)

    def test_age_with_null_date_of_birth_returns_zero(self):
        user = get_user_model().objects.create_user(email='user@mail-domain.com', date_of_birth=None)
        user1 = get_user_model().objects.create_user(email='user1@mail-domain.com', date_of_birth='')

        self.assertEqual(user.age(), 0)
        self.assertEqual(user1.age(), 0)

    def test_age_with_non_null_date_of_birth_returns_expected_age_for_valid_age_unit(self):
        dob = (datetime.now() + timedelta(days=-8395)).strftime(DATE_INPUT_FORMAT)
        user = get_user_model().objects.create_user(email='user@mail-domain.com', date_of_birth=dob)
        self.assertEqual(user.age(unit='years'), 23)
        self.assertEqual(user.age(unit='year'), 23)
        self.assertEqual(user.age(unit='y'), 23)
        self.assertEqual(user.age(unit='m'), 279)  # rounded down to the nearest integer value
        self.assertEqual(user.age(unit='w'), 1199)
        self.assertEqual(user.age(unit='d'), 8395)

    def test_age_with_non_null_date_of_birth_returns_expected_age_for_invalid_age_unit(self):
        """returns days duration by default"""
        dob = (datetime.now() + timedelta(days=-8395)).strftime(DATE_INPUT_FORMAT)
        user = get_user_model().objects.create_user(email='user@mail-domain.com', date_of_birth=dob)
        self.assertEqual(user.age(unit='invalid'), 8395)
