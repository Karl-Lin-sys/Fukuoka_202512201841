from flask import render_template, current_app
from app import mail
from threading import Thread
from flask_mail import Message

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        '[JobBoard] Reset Your Password',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

def send_application_confirmation(application):
    send_email(
        f'Application Submitted: {application.job.title}',
        sender=current_app.config['ADMINS'][0],
        recipients=[application.applicant.email],
        text_body=render_template('email/application_confirmation.txt', 
                                application=application),
        html_body=render_template('email/application_confirmation.html',
                                application=application)
    )

def send_application_notification(application):
    # Send notification to employer
    employer_email = application.job.poster.email
    send_email(
        f'New Application for {application.job.title}',
        sender=current_app.config['ADMINS'][0],
        recipients=[employer_email],
        text_body=render_template('email/new_application.txt', 
                                application=application),
        html_body=render_template('email/new_application.html',
                                application=application)
    )
