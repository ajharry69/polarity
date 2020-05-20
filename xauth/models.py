from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import enums


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
        user = self.__raw_user(email, username, password, first_name, last_name, )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user

    def __raw_user(self, email, username, password, surname=None, first_name=None, last_name=None,
                   mobile_number=None, ):
        if email is None:
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
    __providers = [(k, k) for k, _ in enums.AuthProvider.__members__.items()]
    username = models.CharField(db_index=True, max_length=150, unique=True)
    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)
    surname = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    first_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    last_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    provider = models.CharField(choices=__providers, max_length=20, default=enums.AuthProvider.EMAIL.name)
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
        ordering = ('created_at', 'updated_at',)

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        """
        use email as the username if it wasn't provided
        """
        _username = self.username
        self.username = self.normalize_username(_username if _username and len(_username) > 0 else self.email)
        _password = self.password
        if _password and len(_password) > 0:
            # password was provided
            self.set_password(_password)
        else:
            # password was not provided
            if self.is_superuser:
                # raise error for superuser accounts without password
                raise ValueError('superuser password is required')
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
        return name if name and len(name) > 0 else None

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        name = self.get_full_name()
        if name and isinstance(name, str):
            return name.split()[0] if ' ' in name else name
        return name


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
    temporary_password = models.CharField(max_length=150, blank=False, null=True)
    verification_code = models.CharField(max_length=150, blank=False, null=True)

    def save(self, *args, **kwargs):
        if self.temporary_password and len(self.temporary_password) > 0:
            # probably a password reset was requested, create log
            # Fix. no ip addresses will be attached to this!
            PasswordResetLog.objects.create(user=self.user, )
        super(Metadata, self).save(*args, **kwargs)


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
        Fr3ak241.+#
        Saves access-log without the ambiguity of an access-log being recorded with sign_in and sign_out data in the
        same tuple/row(in a database table) since the two are mutually exclusive events
        """
        if self.sign_in_ip is not None and self.sign_out_ip is None:
            # probably a sign in was done. Just update `time_signed_in` without updating `time_signed_out`
            self.time_signed_in = timezone.now()
            self.time_signed_out = None
            self.sign_out_ip = None
        if self.sign_out_ip is not None and self.sign_in_ip is None:
            # probably a sign out was done. Just update `time_signed_out` without updating `time_signed_in`
            self.time_signed_out = timezone.now()
            self.time_signed_in = None
            self.sign_in_ip = None

        super(AccessLog, self).save(*args, **kwargs)
