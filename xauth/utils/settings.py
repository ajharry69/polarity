from datetime import timedelta

from django.conf import settings
from django.utils.encoding import force_str

try:
    XENTLY_AUTH = settings.XENTLY_AUTH
except AttributeError:
    XENTLY_AUTH = {
        # occasionally included in emails sent by the API to your users for familiarity
        'APP_NAME': 'Xently',
        'TOKEN_KEY': force_str(settings.SECRET_KEY),
        'TOKEN_EXPIRY': timedelta(days=60),
        # string. Email addresses to which account / auth-related replies are to be sent.
        # Also permitted: "Name <email-address>"
        'REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES': [
            settings.EMAIL_HOST_USER
        ],
        # string. Email used to send verification code.
        # Also permitted: "Name <email-address>"
        'ACCOUNTS_EMAIL': settings.EMAIL_HOST_USER,
        'ACCOUNTS_EMAIL_PASSWORD': settings.EMAIL_HOST_PASSWORD,
        'VERIFICATION_CODE_LENGTH': 6,
        'TEMPORARY_PASSWORD_LENGTH': 8,
        'VERIFICATION_CODE_EXPIRY': timedelta(hours=1),
        'TEMPORARY_PASSWORD_EXPIRY': timedelta(minutes=30),
        # period within which a user is considered new since account creation date
        'NEWBIE_VALIDITY_PERIOD': timedelta(days=1),
        'AUTO_HASH_PASSWORD_ON_SAVE': True,
    }
