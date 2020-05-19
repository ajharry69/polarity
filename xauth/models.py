from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

from .utils import enums


class UserManager(BaseUserManager):
    def create_user(
            self, email,
            username=None,
            mobile_number=None,
            surname=None,
            first_name=None,
            last_name=None,
            password=None, ):
        if email is None:
            raise ValueError('email is required')

        # use email as the username if it wasn't provided
        _username = email if username is None else username
        user = self.model(
            email=self.normalize_email(email),
            username=_username,
            mobile_number=mobile_number,
            surname=surname,
            first_name=first_name,
            last_name=last_name,
        )
        if password is not None:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, first_name=None, ):
        if password is None:
            raise ValueError('superuser password is required')
        user = self.create_user(email, username, password=password, first_name=first_name)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()
        return user


class User(AbstractBaseUser):
    __sign_in_methods = [(k, k) for k, _ in enums.SignInMethod.__members__.items()]
    username = models.EmailField(db_index=True, max_length=150, unique=True)
    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)
    surname = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    first_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    last_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    sign_in_method = models.CharField(choices=__sign_in_methods, max_length=20, default=enums.SignInMethod.EMAIL.name)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'  # returned by get_email_field_name()

    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        name = f'{self.surname} {self.first_name} {self.last_name}'.strip()
        # TODO: trim off spaces at the start or end
        name = name  # name after trim off
        if len(name) < 1:
            # name is empty, use username instead
            name = self.username
        return name

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        name = self.first_name
        if name is None or len(name) < 1:
            # name is empty, use username instead
            name = self.username
        return name
