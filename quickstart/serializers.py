"""
Used for our data representations
"""
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # not necessary if `app_name` is not provided in `url.py`
    url = serializers.HyperlinkedIdentityField(view_name='quickstart:user-detail')
    # not necessary if `app_name` is not provided in `url.py`
    groups = serializers.HyperlinkedRelatedField(view_name='quickstart:group-detail', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    # not necessary if `app_name` is not provided in `url.py`
    url = serializers.HyperlinkedIdentityField(view_name='quickstart:group-detail')

    class Meta:
        model = Group
        fields = ['url', 'name']
