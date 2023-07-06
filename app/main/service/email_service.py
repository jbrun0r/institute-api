from threading import Thread

from flask import copy_current_request_context, render_template, current_app
from flask_mail import Message

from app.main import mail


def send_email(
    email: str,
    template_name: str,
    message_subject: str,
    body: str = None,
    **context: any
):
    """Send an email asynchronously.
    
    Args:
        email (str): Recipient email address.
        template_name (str): Name of the email template.
        message_subject (str): Subject of the email.
        body (str, optional): Plain text body of the email. Defaults to None.
        **context (any): Additional context variables to be passed to the email template.
    """
    msg = Message(
        subject=message_subject,
        body=body,
        recipients=[email],
        html=render_template(template_name, **context)
    )

    if current_app.config['ENV'] != 'testing':
        @copy_current_request_context
        def send():
            mail.send(msg)
            return
        Thread(target=send).start()
