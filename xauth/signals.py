from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.utils import timezone

from xauth.models import PasswordResetLog, AccessLog


def _create_password_reset_log(user):
    try:
        # get latest log for `user`
        reset_log = PasswordResetLog.objects.filter(user=user, ).order_by('-request_time')[0]
        reset_log.change_time = timezone.now()
        reset_log.save()
    except IndexError:
        # reset log for `user` not found, create
        PasswordResetLog.objects.create(user=user, )


def _create_access_log(user):
    AccessLog.objects.create(user=user, sign_in_time=timezone.now())


def on_user_pre_save(sender, instance, **kwargs):
    """creates access & password reset log(s)"""
    try:
        user = get_user_model().objects.get(pk=instance.pk)
        last_login = user.last_login
        if user.check_password(instance.password) is False:
            # password is probably been changed and a change request was previously made
            _create_password_reset_log(instance)

        if last_login and last_login != instance.last_login:
            # the user probably just logged in
            _create_access_log(instance)

    except get_user_model().DoesNotExist:
        pass


def on_user_post_save(sender, instance, created, **kwargs):
    """
    Checks if `instance`(user) is marked as un-verified and send an email with verification code
    """
    user = instance
    if not user.is_verified:
        user.request_verification()


pre_save.connect(on_user_pre_save, sender=get_user_model(), dispatch_uid='1')
post_save.connect(on_user_post_save, sender=get_user_model(), dispatch_uid='2')
