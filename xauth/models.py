import json

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import enums, valid_str
from .utils.mail import Mail
from .utils.settings import *
from .utils.token import Token

PASSWORD_LENGTH = 128


class UserManager(BaseUserManager):
    def create_user(
            self, email,
            username=None,
            password=None,
            surname=None,
            first_name=None,
            last_name=None,
            mobile_number=None, ):
        user = self.__raw_user(email, username, password, surname, first_name, last_name, mobile_number, )
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, first_name=None, last_name=None, ):
        user = self.__raw_user(email, username, password, first_name=first_name, last_name=last_name, )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user

    def __raw_user(self, email, username, password, surname=None, first_name=None, last_name=None,
                   mobile_number=None, ):
        if not valid_str(email):
            raise ValueError('email is required')
        return self.model(
            email=self.normalize_email(email),
            username=username,
            mobile_number=mobile_number,
            surname=surname,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )


class User(AbstractBaseUser, PermissionsMixin):
    """
    Guidelines: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
    """
    __NEWBIE_GP = XENTLY_AUTH.get('NEWBIE_VALIDITY_PERIOD', None)
    __AUTO_HASH = XENTLY_AUTH.get('AUTO_HASH_PASSWORD_ON_SAVE', True)
    __PROVIDERS = [(k, k) for k, _ in enums.AuthProvider.__members__.items()]
    username = models.CharField(db_index=True, max_length=150, unique=True)
    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)
    surname = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    first_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    last_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    provider = models.CharField(choices=__PROVIDERS, max_length=20, default=enums.AuthProvider.EMAIL.name)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'  # returned by get_email_field_name()

    # all the fields listed here(including the USERNAME_FIELD and password) are
    # expected as part of parameters in `objects`(UserManager).create_superuser
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', ]

    class Meta:
        ordering = ('created_at', 'updated_at', 'username',)

    def __str__(self):
        return self.get_full_name()

    def __repr__(self):
        return json.dumps(self._jsonified())

    def save(self, auto_hash_password=__AUTO_HASH, *args, **kwargs):
        """
        use email as the username if it wasn't provided
        :param auto_hash_password if True, `self.password` will be hashed before saving to database
        """
        _username = self.username
        self.username = self.normalize_username(_username if _username and len(_username) > 0 else self.email)
        if auto_hash_password is True:
            self.__reinitialize_password_with_hash()
        self.is_verified = self.__get_ascertained_verification_status()
        super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        s_name = self.surname.strip().capitalize() if self.surname else ''
        f_name = self.first_name.strip().capitalize() if self.first_name else ''
        l_name = self.last_name.strip().capitalize() if self.last_name else ''
        # trim off spaces at the start and/or end
        name = f'{s_name} {f_name} {l_name}'.strip()
        if len(name) < 1:
            # name is empty, use username instead
            name = self.username
        return name if name and valid_str(name) else None

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        name = self.get_full_name()
        if valid_str(name):
            return name.split()[0] if ' ' in name else name
        return name

    def is_newbie(self, period: timedelta = __NEWBIE_GP):
        """
        Flags user as a new if account(user object) is lasted for at most `period`
        since the value of `self.created_at`
        :return: bool. `True` if considered new `False` otherwise
        """
        period = timedelta(seconds=15) if period is None else period
        now = timezone.now()
        return now >= self.created_at >= (now - period)

    # Used in django admin site
    is_newbie.admin_order_field = 'created_at'
    is_newbie.boolean = True
    is_newbie.short_description = 'Newbie?'

    @staticmethod
    def get_random_code(alpha_numeric: bool = True, length=None):
        """
        Generates and returns random code of `length`
        :param alpha_numeric: if `True`, include letters and numbers in the generated code
        otherwise return only numbers
        :param length: length of the code. Random number between 8 & 10 will be used if not
        provided
        :return: random code
        """
        import random
        length = random.randint(8, 10) if length is None or not isinstance(length, int) else length
        rand = None
        if alpha_numeric:
            rand = User.objects.make_random_password(length=length)
        else:
            rand = User.objects.make_random_password(length=length, allowed_chars='23456789')
        return rand

    @property
    def public_serializable_fields(self):
        return [
            'username',
            'email',
            'surname',
            'first_name',
            'last_name',
            'mobile_number',
            'provider',
            'is_superuser',
            'is_staff',
            'is_verified',
            'created_at',
        ]

    @property
    def readonly_serializable_fields(self):
        return [
            'username',
            'email',
            'is_superuser',
            'is_staff',
            'is_verified',
            'created_at',
        ]

    def reset_password(self, temporary_password, new_password):
        """
        :param temporary_password: raw temporary password to be verified against database's temporary password
         for correctness(match)
        :param new_password: what should be used as the new password if temporary password matches database's
        temporary password
        :return: tuple (Token, message) if user's account was reset successfully (Token, None) else (None,
        Non-None-message)
        """
        try:
            metadata = Metadata.objects.get(pk=self.id)
            if metadata.is_temporary_password_expired:
                return None, 'expired'
            if metadata.check_temporary_password(raw_password=temporary_password):
                # temporary password matched(correct)
                # update user's password
                self.password = new_password
                # prevent hashing of other irrelevant table column(s)
                self.save(update_fields=['password'])
                # reset temporary password & password generation time to None
                metadata.temporary_password = None
                metadata.tp_gen_time = None
                # prevent hashing of other irrelevant table column(s)
                metadata.save(update_fields=['temporary_password', 'tp_gen_time'])
                return self.token, None
            else:
                # temporary password mismatched(incorrect)
                return None, 'incorrect'
        except Metadata.DoesNotExist:
            return None, 'user not found'

    def verify(self, code):
        """
        :param code: raw verification code to be verified against database's verification code for correctness
        (match)
        :return: tuple (Token, message) if user's account was verified successfully (Token, None) else (Token,
        Non-None-message)
        """
        if self.is_verified:
            # no need of repeating the task
            return self.token, None
        try:
            metadata = Metadata.objects.get(pk=self.id)
            if metadata.is_verification_code_expired:
                return None, 'expired'
            if metadata.check_verification_code(raw_code=code):
                # verification code matched(correct)
                # update user's verification status
                self.is_verified = True
                # prevent's automatic hashing of irrelevant password
                self.save(auto_hash_password=False, update_fields=['is_verified'])
                # reset verification code & code generation time to None
                metadata.verification_code = None
                metadata.vc_gen_time = None
                # prevent hashing of other irrelevant table column(s)
                metadata.save(update_fields=['verification_code', 'vc_gen_time'])
                return self.token, None
            else:
                # verification code mismatched(incorrect)
                return None, 'incorrect'
        except Metadata.DoesNotExist:
            return None, 'user not found'

    @property
    def token(self):
        expiry = XENTLY_AUTH.get('TOKEN_EXPIRY', timedelta(days=60))
        return Token(self._jsonified(), expiry_period=expiry)

    @property
    def password_reset_token(self):
        """
        :return: dict of containing pair of encrypted and unencrypted(normal) token for password reset
        """
        expiry = XENTLY_AUTH.get('TEMPORARY_PASSWORD_EXPIRY', timedelta(minutes=30))
        return Token(self._jsonified(), expiry_period=expiry)

    @property
    def verification_token(self):
        """
        :return: dict of containing pair of encrypted and unencrypted(normal) token for user account
        verification
        """
        expiry = XENTLY_AUTH.get('VERIFICATION_CODE_EXPIRY', timedelta(hours=1))
        return Token(self._jsonified(), expiry_period=expiry)

    def request_password_reset(self, send_mail: bool = False):
        """
        Sends account password reset email with temporary password
        :return: tuple of (`Token`, temporary-password)
        """
        length = XENTLY_AUTH.get('TEMPORARY_PASSWORD_LENGTH', 8)
        # random temporary password of `length`
        password = self.get_random_code(length=length)

        if send_mail:
            # send user email
            subject = 'Password Reset'
            plain, formatted = Mail.Templates.password_reset(self, password)
            body = Mail.Body(plain=plain, formatted=formatted)
            self.send_email(subject, body)

        # store the verification request data to database
        metadata, _ = Metadata.objects.get_or_create(user_id=self.id)
        metadata.temporary_password = password
        metadata.tp_gen_time = timezone.now()
        metadata.save()
        return self.password_reset_token, password

    def request_verification(self, send_mail: bool = False):
        """
        Sends account verification email with verification code
        :return: tuple of (`Token`, verification-code)
        """
        length = XENTLY_AUTH.get('VERIFICATION_CODE_LENGTH', 6)
        # random verification code of `length`
        code = self.get_random_code(alpha_numeric=False, length=length)

        # get or create a metadata object for the `user`
        metadata, created = Metadata.objects.get_or_create(user_id=self.id)

        if send_mail:
            # send user email
            # show welcome if the user is new and and is just created a metadata object in db
            show_welcome = self.is_newbie() and created
            subject = 'Account Verification'
            plain, formatted = Mail.Templates.account_verification(self, code, show_welcome)
            body = Mail.Body(plain=plain, formatted=formatted)
            self.send_email(subject, body)

        # store the verification request data to database
        metadata.verification_code = code
        metadata.vc_gen_time = timezone.now()
        metadata.save()
        return self.verification_token, code

    def send_email(self, subject, body: Mail.Body):
        sender_address = XENTLY_AUTH.get('ACCOUNTS_EMAIL')
        reply_addresses = XENTLY_AUTH.get('REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES')
        Mail.send(subject, body, address=Mail.Address(self.email, sender=sender_address, reply_to=reply_addresses))

    def _jsonified(self):
        return dict(
            username=self.username,
            email=self.email,
            surname=self.surname,
            first_name=self.first_name,
            last_name=self.last_name,
            mobile_number=self.mobile_number,
            provider=self.provider,
            is_superuser=self.is_superuser,
            is_staff=self.is_staff,
            is_verified=self.is_verified,
            created_at=self.created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
        )

    def _hash_code(self, raw_code: str):
        """
        Uses `settings.PASSWORD_HASHERS` to create and return a hashed `code` just like creating a hashed
        password

        :param raw_code: data to be hashed
        :return: hashed version of `code`
        """
        # temporarily hold the user's password
        acc_password = self.password
        # hash the code
        self.set_password(raw_code)  # will reinitialize the password
        code = self.password  # hashed code retrieved from password
        # re-[instate|initialize] user's password to it's previous value
        self.password = acc_password
        return code

    def __reinitialize_password_with_hash(self):
        _password = self.password
        if valid_str(_password):
            # password was provided
            self.set_password(_password)
        else:
            # password was not provided
            if self.is_superuser:
                # raise error for superuser accounts without password
                raise ValueError('superuser password is required')
            self.set_unusable_password()

    def __get_ascertained_verification_status(self):
        """
        :returns correct verification status based on 'user type'(superuser/staff) and `self.provider`
        """
        verified = self.is_verified
        if not verified:
            # check if it might have been a false-alarm on verification status
            if self.provider not in [enums.AuthProvider.EMAIL.name, enums.AuthProvider.PHONE.name]:
                # credentials must have already been verified by the auth provider
                verified = True
            if self.is_superuser or self.is_staff:
                # probably a known user already
                verified = True
        return verified


class PasswordResetLog(models.Model):
    __reset_types = [(k, k) for k, _ in enums.PasswordResetType.__members__.items()]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(choices=__reset_types, max_length=10, default=enums.PasswordResetType.RESET.name)
    request_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    change_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    request_time = models.DateTimeField(default=timezone.now)
    change_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-request_time', '-change_time', '-request_ip', '-change_ip',)


# noinspection PyUnresolvedReferences,PyProtectedMember
class Metadata(models.Model):
    """
    TODO: 1. mark `user` as verified or unverified if verification_code is updated to `null` or
        `!null` respectively
        2. create a password reset log when temporary
    Contains additional data used for user account 'house-keeping'

    :cvar temporary_password hashed short-live password expected to be used for password reset

    :cvar verification_code hashed short-live code expected to be used for account verification
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, )
    temporary_password = models.CharField(max_length=PASSWORD_LENGTH, blank=False, null=True)
    verification_code = models.CharField(max_length=PASSWORD_LENGTH, blank=False, null=True)
    tp_gen_time = models.DateTimeField(_('temporary password generation time'), blank=True, null=True)
    vc_gen_time = models.DateTimeField(_('verification code generation time'), blank=True, null=True)

    def save(self, *args, **kwargs):
        raw_password = self.temporary_password
        raw_code = self.verification_code
        if valid_str(raw_code):
            self.verification_code = self._hash_code(raw_code)
        if valid_str(raw_password):
            self.temporary_password = self._hash_code(raw_password)
            # probably a password reset was requested, create log
            # Fix. no ip addresses will be attached to this!
            PasswordResetLog.objects.create(user=self.user, )
        super(Metadata, self).save(*args, **kwargs)

    @property
    def is_verification_code_expired(self):
        expiry = XENTLY_AUTH.get('VERIFICATION_CODE_EXPIRY', timedelta(hours=1))
        return (self.vc_gen_time + expiry) <= timezone.now()

    @property
    def is_temporary_password_expired(self):
        expiry = XENTLY_AUTH.get('TEMPORARY_PASSWORD_EXPIRY', timedelta(minutes=30))
        return (self.tp_gen_time + expiry) <= timezone.now()

    def check_temporary_password(self, raw_password) -> bool:
        """:returns True if `raw_password` matches `self.temporary_password`"""
        return self.__verify_this_against_other_code(self.temporary_password, raw_password)

    def check_verification_code(self, raw_code) -> bool:
        """:returns True if `raw_code` matches `self.verification_code`"""
        return self.__verify_this_against_other_code(self.verification_code, raw_code)

    def __verify_this_against_other_code(self, this, other):
        user = self.user
        user.password = this
        return user.check_password(other)

    def _hash_code(self, raw_code):
        return self.user._hash_code(raw_code)


class AccessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sign_in_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    sign_out_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    sign_in_time = models.DateTimeField(blank=True, null=True)
    sign_out_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-sign_in_ip', '-sign_out_ip', '-sign_in_time', '-sign_out_time',)

    def save(self, *args, **kwargs):
        """
        Saves access-log without the ambiguity of an access-log being recorded with sign_in and sign_out data in the
        same tuple/row(in a database table) since the two are mutually exclusive events
        """
        if valid_str(self.sign_in_ip) and not valid_str(self.sign_out_ip):
            # probably a sign in was done. Just update `time_signed_in` without updating `time_signed_out`
            self.time_signed_in = timezone.now()
            self.time_signed_out = None
            self.sign_out_ip = None
        if valid_str(self.sign_out_ip) and not valid_str(self.sign_in_ip):
            # probably a sign out was done. Just update `time_signed_out` without updating `time_signed_in`
            self.time_signed_out = timezone.now()
            self.time_signed_in = None
            self.sign_in_ip = None

        super(AccessLog, self).save(*args, **kwargs)
