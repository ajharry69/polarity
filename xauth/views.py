import re

from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions, generics, views, status
from rest_framework.response import Response

from .permissions import *
from .serializers import *
from .utils import get_204_wrapped_response, get_wrapped_response


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsSuperUser, IsAuthenticatedAndOwner, ]

    def get(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().get(request, *args, **kwargs))

    def put(self, request, *args, **kwargs):
        return get_wrapped_response(super().put(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        return get_wrapped_response(super().patch(request, *args, **kwargs))

    def delete(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().delete(request, *args, **kwargs))

    def perform_update(self, serializer):
        serializer.save(auto_hash_password=False)


class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):
        return get_wrapped_response(super().post(request, *args, **kwargs))


class SignInView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    @staticmethod
    def post(request, format=None):
        # authentication logic is by default handled by the auth-backend
        serializer = AuthSerializer(request.user, context={'request': request}, )
        return get_wrapped_response(Response(serializer.data, status=status.HTTP_200_OK))


class VerificationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    @staticmethod
    def post(request, format=None):
        user = request.user
        operation = request.query_params.get('operation', 'verify').lower()
        if re.match('^(re(send|quest)|send)$', operation):
            # new verification code resend or request is been made
            token, code = user.request_verification(send_mail=True)
            serializer = AuthTokenOnlySerializer(user, )
        else:
            # verify provided code
            code = request.data.get('code', None)
            token, message = user.verify(code=code)
            if token is not None:
                # verification was successful
                # TODO: Verify that returned token is not verification-token
                serializer = AuthTokenOnlySerializer(user, )
            else:
                return Response({
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetView(views.APIView):
    permission_classes = [permissions.AllowAny, ]

    @staticmethod
    def post(request, format=None):
        # should contain a user object if Token authentication(from AuthBackend) was successful
        user = request.user
        data = request.data
        operation = request.query_params.get('operation', 'reset').lower()
        if (isinstance(user, AnonymousUser) or user is None) or re.match('^(re(send|quest)|send)$', operation):
            # probably a new request for password reset
            # get username to resend the email
            username = data.get('username', None)
            try:
                user = get_user_model().objects.get_by_natural_key(username=username)
                token, message = user.request_password_reset(send_mail=True)
                return Response(token.tokens, status=status.HTTP_200_OK)
            except get_user_model().DoesNotExist:
                # user not found
                return Response({
                    'error': 'user account does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # reset password
            t_pass = data.get('temporary_password', data.get('old_password', None))
            n_pass = data.get('new_password', None)
            token, message = user.reset_password(temporary_password=t_pass, new_password=n_pass)
            if token is not None:
                # password reset was successful
                # TODO: Verify that returned token is not password-reset-token
                serializer = AuthTokenOnlySerializer(user, )
            else:
                return Response({
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
