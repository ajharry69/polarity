"""
Used for our data representations
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # not necessary if `app_name` is not provided in `url.py`
    url = serializers.HyperlinkedIdentityField(view_name='quickstart:user-detail')
    # not necessary if `app_name` is not provided in `url.py`
    groups = serializers.HyperlinkedRelatedField(view_name='quickstart:group-detail', many=True, read_only=True)
    token = serializers.DictField(source='token.tokens', read_only=True, )

    class Meta:
        model = get_user_model()
        # fields = ['url', 'username', 'email', 'groups']
        # assumption is made that get_user_model() is an instance of `xauth.models.User`
        fields = get_user_model().PUBLIC_READ_WRITE_FIELDS + ('url', 'groups', 'token',)
        read_only_fields = get_user_model().READ_ONLY_FIELDS


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    # not necessary if `app_name` is not provided in `url.py`
    url = serializers.HyperlinkedIdentityField(view_name='quickstart:group-detail')

    class Meta:
        model = Group
        fields = ['url', 'name']
