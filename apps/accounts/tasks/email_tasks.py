from celery import shared_task

@shared_task
def send_otp_email(email, otp):
    """Send OTP email (console output for demo)"""
    print(f"=== OTP EMAIL ===")
    print(f"To: {email}")
    print(f"Subject: Your OTP Code")
    print(f"Your OTP code is: {otp}")
    print(f"This code will expire in 5 minutes.")
    print(f"================")
    return f"OTP email sent to {email}"