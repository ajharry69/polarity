from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from xauth.models import Metadata, SecurityQuestion


def create_user(username):
    return get_user_model().objects.create_user(username=username, email=f'{username}@mail-domain.com')


def update_metadata(user, sec_quest=None, sec_ans=None, tpass=None, vcode=None, tp_gen: timedelta = None,
                    vc_gen: timedelta = None):
    meta, created = Metadata.objects.get_or_create(user=user)
    if sec_quest:
        meta.security_question = sec_quest
    if sec_ans:
        meta.security_question_answer = sec_ans
    meta.temporary_password = tpass
    meta.tp_gen_time = timezone.now() + (tp_gen if tp_gen is not None else timedelta(seconds=0))
    meta.verification_code = vcode
    meta.vc_gen_time = timezone.now() + (vc_gen if vc_gen is not None else timedelta(seconds=0))
    meta.save()

    return meta


def create_security_question(question: str = 'What is your favourite color?', usable: bool = True):
    return SecurityQuestion.objects.create(question=question, usable=usable)
