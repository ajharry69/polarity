from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from xauth.models import Metadata


def _create_user(username):
    return get_user_model().objects.create_user(username=username, email=f'{username}@mail-domain.com')


def _create_metadata(user, tpass=None, vcode=None, tp_gen: timedelta = None, vc_gen: timedelta = None):
    meta = Metadata.objects.get_or_create(user=user)[0]
    meta.temporary_password = tpass
    meta.tp_gen_time = timezone.now() + (tp_gen if tp_gen is not None else timedelta(seconds=0))
    meta.verification_code = vcode
    meta.vc_gen_time = timezone.now() + (vc_gen if vc_gen is not None else timedelta(seconds=0))
    meta.save()

    return meta


class MetadataTestCase(APITestCase):
    user = None

    def setUp(self) -> None:
        self.user = _create_user('mitch')

    def test_check_temporary_password_returns_true_for_correct_password(self):
        password = 'password'
        meta = _create_metadata(self.user, tpass=password)

        self.assertIs(meta.check_temporary_password(raw_password=password), True)
        self.assertIs(meta.check_temporary_password(raw_password='password12'), False)

    def test_check_verification_code_returns_true_for_correct_code(self):
        code = '123456'
        meta = _create_metadata(self.user, vcode=code)

        self.assertIs(meta.check_verification_code(raw_code=code), True)
        self.assertIs(meta.check_verification_code(raw_code='654321'), False)

    def test_is_temporary_password_expired_returns_true_for_period_longer_than_30minutes_since_gen_time(self):
        password = 'password'
        tp_gen = timedelta(minutes=-30, seconds=-1)
        meta = _create_metadata(self.user, tpass=password, tp_gen=tp_gen)

        self.assertIs(meta.is_temporary_password_expired, True)

    def test_is_verification_code_expired_returns_true_for_period_longer_than_1hour_since_gen_time(self):
        code = '123456'
        vc_gen = timedelta(hours=-1, seconds=-1)
        meta = _create_metadata(self.user, vcode=code, vc_gen=vc_gen)

        self.assertIs(meta.is_verification_code_expired, True)

    def test_is_temporary_password_expired_returns_false_for_period_within_30minutes_since_gen_time(self):
        password = 'password'
        tp_gen = timedelta(seconds=1)
        meta = _create_metadata(self.user, tpass=password, tp_gen=tp_gen)

        self.assertIs(meta.is_temporary_password_expired, False)

    def test_is_verification_code_expired_returns_false_for_period_within_1hour_since_gen_time(self):
        code = '123456'
        vc_gen = timedelta(seconds=1)
        meta = _create_metadata(self.user, vcode=code, vc_gen=vc_gen)

        self.assertIs(meta.is_verification_code_expired, False)
