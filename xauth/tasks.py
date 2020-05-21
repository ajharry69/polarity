from celery import shared_task


@shared_task
def send_mail_async(subject: str, body_p: str, body_f: str, recipients: list, sender: str, reply_to: list, ):
    """
    Asynchronously send mail with a body compose of a plain and an alternative HTML formatted-body
    """
    from django.core.mail import EmailMultiAlternatives
    mc = EmailMultiAlternatives(subject=subject, body=body_p, from_email=sender, to=recipients, reply_to=reply_to)
    mc.attach_alternative(body_f, "text/html")
    mc.send()

    # from django.core.mail import send_mail
    # send_mail(subject=subject, message=body_p, html_message=body_f, from_email=sender, recipient_list=recipients,
    #           auth_password=sender_password, )
