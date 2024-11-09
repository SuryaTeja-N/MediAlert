from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app
import os

def send_email(to_email, subject, content):
    try:
        sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        message = Mail(
            from_email=current_app.config['MAIL_DEFAULT_SENDER'],
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False 