from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.models import SecurityQuestion


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile')

    # groups = serializers.HyperlinkedRelatedField(view_name='group-detail', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = get_user_model().PUBLIC_READ_WRITE_FIELDS + ('url',)
        read_only_fields = get_user_model().READ_ONLY_FIELDS


class AuthTokenOnlySerializer(serializers.HyperlinkedModelSerializer):
    normal = serializers.CharField(source='token.tokens.normal', read_only=True, )
    encrypted = serializers.CharField(source='token.tokens.encrypted', read_only=True, )

    class Meta:
        model = get_user_model()
        fields = 'normal', 'encrypted',


class AuthSerializer(AuthTokenOnlySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile')

    class Meta(AuthTokenOnlySerializer.Meta):
        fields = ProfileSerializer.Meta.fields + AuthTokenOnlySerializer.Meta.fields
        read_only_fields = ProfileSerializer.Meta.read_only_fields

    def validate(self, attrs):
        return super().validate(attrs)


class SignUpSerializer(AuthSerializer):
    password = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, )

    class Meta(AuthSerializer.Meta):
        fields = AuthSerializer.Meta.fields + get_user_model().WRITE_ONLY_FIELDS


class SecurityQuestionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:securityquestion-detail')
    date_added = serializers.DateTimeField(source='added_on', read_only=True, )
    usable = serializers.BooleanField(default=True, )

    class Meta:
        model = SecurityQuestion
        fields = ('url', 'question', 'usable', 'date_added',)
