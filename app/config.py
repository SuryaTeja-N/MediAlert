import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Gmail SMTP Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('GMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('GMAIL_USERNAME')
    MAIL_USE_SSL = False
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False