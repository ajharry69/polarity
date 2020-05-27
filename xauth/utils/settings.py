from django.conf import settings

try:
    XENTLY_AUTH = settings.XAUTH
except AttributeError:
    XENTLY_AUTH = {}

try:
    DATE_INPUT_FORMAT = settings.DATE_INPUT_FORMATS[0]
except (IndexError, AttributeError):
    DATE_INPUT_FORMAT = '%Y-%m-%d'
