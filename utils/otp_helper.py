import os
from twilio.rest import Client

def send_otp_sms(otp):
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE")
    fixed_number = os.getenv("OTP_FIXED_NUMBER")

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your BBBS registration OTP is: {otp}",
        from_=twilio_number,
        to=fixed_number
    )

    return message.sid
