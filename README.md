# Welcome to django-xently-rest-auth

[![Build Status](https://travis-ci.com/ajharry69/polarity.svg?branch=auth-api)](https://travis-ci.com/ajharry69/polarity)
[![Coverage Status](https://coveralls.io/repos/github/ajharry69/polarity/badge.svg?branch=auth-api)](https://coveralls.io/github/ajharry69/polarity?branch=auth-api)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/26f09088f70f46eda61633306b2147de)](https://app.codacy.com/manual/ajharry69/polarity?utm_source=github.com&utm_medium=referral&utm_content=ajharry69/polarity&utm_campaign=Badge_Grade_Dashboard)
[![Documentation Status](https://readthedocs.org/projects/polarity/badge/?version=latest)](https://polarity.readthedocs.io/en/latest/?badge=latest)

A [Django](https://github.com/django/django) token-based authentication framework.

## Features
Checked features are ones already implemented

- [x] Additional helper methods added to `User` model
    - [x] optional automatic password hashing during `User` creation
- [x] Optional account access per (provided) device's ip-address logging
- [x] Optional password reset per (provided) device's ip-address logging
- [x] Generate jwt tokens
    - [x] encrypted
    - [x] unencrypted
- [x] Password reset
    - [x] Generate hashed temporary password
    - [x] Optionally send temporary password via email
    - [x] Limit temporary password validity period
    - [x] Helper functions to help reset password
- [x] Account verification
    - [x] Generate hashed verification code
    - [x] Optionally send verification via email
    - [x] Limit verification code validity period
    - [x] Helper functions to help verify account

## Getting started
Add the following to your Django project's `settings.py` file

```python
AUTH_USER_MODEL = 'xauth.User'
INSTALLED_APPS = [
'xauth'
]
XENTLY_AUTH = {
    # occasionally included in emails sent by the API to your users for familiarity
    'APP_NAME': 'Xently',
    'TOKEN_KEY': 'force_str(SECRET_KEY)',
    'TOKEN_EXPIRY': 'timedelta(days=60)',
    # string. Email addresses to which account / auth-related replies are to be sent.
    # Also permitted: "Name <email-address>"
    'REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES': [
        'settings.EMAIL_HOST_USER'
    ],
    # string. Email used to send verification code.
    # Also permitted: "Name <email-address>"
    'ACCOUNTS_EMAIL': 'settings.EMAIL_HOST_USER',
    'ACCOUNTS_EMAIL_PASSWORD': 'settings.EMAIL_HOST_PASSWORD',
    'VERIFICATION_CODE_LENGTH': 6,
    'TEMPORARY_PASSWORD_LENGTH': 8,
    'VERIFICATION_CODE_EXPIRY': 'timedelta(hours=1)',
    'TEMPORARY_PASSWORD_EXPIRY': 'timedelta(minutes=30)',
    # period within which a user is considered new since account creation date
    'NEWBIE_VALIDITY_PERIOD': 'timedelta(days=1)',
    'AUTO_HASH_PASSWORD_ON_SAVE': True,
}
```