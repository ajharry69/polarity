from django.contrib.auth.models import User
from rest_framework import serializers

from .models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # variable/property must match the `related_name` provided in model class OR
    # provide a `source`(key-word argument) with value being the `related_name`
    # in model class here
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippets:snippet-detail', read_only=True)
    # not necessary if `app_name` is not provided in `url.py`
    url = serializers.HyperlinkedIdentityField(view_name='snippets:user-detail')

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # In a `ViewSet`, `view_name` value must be in the form of {model-name}-{custom-view-action-name}
    # variable name can be any anything
    highlight = serializers.HyperlinkedIdentityField(view_name='snippets:snippet-highlight', format='html')
    # not necessary if `app_name` is not provided in `url.py`
    url = serializers.HyperlinkedIdentityField(view_name='snippets:snippet-detail')

    class Meta:
        model = Snippet
        fields = [
            'url',
            'id',
            'created',
            'title',
            'code',
            'linenos',
            'language',
            'style',
            'highlight',
            # 'highlighted',
            'owner',
        ]
