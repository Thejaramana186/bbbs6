import os
from flask_mail import Message
from app import mail

def send_otp_email(otp):
    admin_email = os.getenv("OTP_RECEIVER_EMAIL")
    
    msg = Message(
        subject="BBBS Registration OTP",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[admin_email],
        body=f"New Registration OTP: {otp}"
    )

    mail.send(msg)
