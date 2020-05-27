import re

from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions, generics, views, status, viewsets
from rest_framework.response import Response

from .permissions import *
from .serializers import *
from .utils import get_204_wrapped_response, get_wrapped_response


class SecurityQuestionView(viewsets.ModelViewSet):
    queryset = SecurityQuestion.objects.filter(usable=True)
    serializer_class = SecurityQuestionSerializer
    permission_classes = [IsSuperUserOrReadOnly, ]


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, ]

    def get(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().get(request, *args, **kwargs))

    def put(self, request, *args, **kwargs):
        return get_wrapped_response(super().put(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        return get_wrapped_response(super().patch(request, *args, **kwargs))

    def delete(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().delete(request, *args, **kwargs))

    def perform_update(self, serializer):
        serializer.save(auto_hash_password=False)  # TODO: seem to be having no effect


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


class VerificationCodeSendView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, format=None):
        user = request.user
        # new verification code resend or request is been made
        token, code = user.request_verification(send_mail=True)
        response = Response(AuthTokenOnlySerializer(user, ).data, status=status.HTTP_200_OK)
        return get_wrapped_response(response)


class VerificationCodeVerifyView(VerificationCodeSendView):
    """
    Attempts to verify authenticated user's verification code(retrieved from a POST request using
    'code' as key).

    =============================================================================================

    From the same POST request user can add a `query_param` with **key** = 'operation' and value
    being one of ['send', 'resend', 'request'] to be sent a new verification code

    =============================================================================================
    """

    def post(self, request, format=None):
        user = request.user
        operation = request.query_params.get('operation', 'verify').lower()
        if re.match('^(re(send|quest)|send)$', operation):
            # new verification code resend or request is been made
            return super(VerificationCodeVerifyView, self).post(request, format)
        else:
            # verify provided code
            code = request.data.get('code', None)
            token, message = user.verify(code=code)
            if token is not None:
                # verification was successful
                data, status_code = AuthTokenOnlySerializer(user, ).data, None
            else:
                data, status_code = {'error': message}, status.HTTP_400_BAD_REQUEST
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)


class PasswordResetSendView(views.APIView):
    permission_classes = [permissions.AllowAny, ]

    @staticmethod
    def post(request, format=None):
        email = request.data.get('email', None)
        try:
            user = request.user
            is_valid_user = user and not isinstance(user, AnonymousUser)
            user = user if is_valid_user else get_user_model().objects.get(email=email)
            token, message = user.request_password_reset(send_mail=True)
            data, status_code = token.tokens, status.HTTP_200_OK
        except get_user_model().DoesNotExist:
            # user not found
            data, status_code = {'error': 'email address is not registered'}, status.HTTP_404_NOT_FOUND
        return get_wrapped_response(Response(data, status=status_code))


class PasswordResetView(PasswordResetSendView):
    """
    Attempts to reset(change) authenticated user's password(retrieved from a POST request using
    `temporary_password` as key).

    =============================================================================================

    From the same POST request user can add a `query_param` with **key** = 'operation' and
    **value** being one of ['send', 'resend', 'request'] to be sent a new **temporary password**

    =============================================================================================
    """
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, format=None):
        # should contain a user object if Token authentication(from AuthBackend) was successful
        user, data = request.user, request.data
        operation = request.query_params.get('operation', 'reset').lower()
        if re.match('^(re(send|quest)|send)$', operation):
            # probably a new request for password reset
            # get username to resend the email
            return super(PasswordResetView, self).post(request, format)
        else:
            # reset password
            t_pass = data.get('temporary_password', data.get('old_password', None))
            n_pass = data.get('new_password', None)
            token, message = user.reset_password(temporary_password=t_pass, new_password=n_pass)
            if token is not None:
                # password reset was successful
                data, status_code = AuthTokenOnlySerializer(user, ).data, None
            else:
                data, status_code = {'error': message}, status.HTTP_400_BAD_REQUEST
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)
