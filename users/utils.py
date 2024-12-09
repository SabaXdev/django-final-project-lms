import random
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, request):
    otp = random.randint(100000, 999999)
    print(f"User Email: {user.email}")  # This will print the email to the console
    user_email = 'sabakatamadze@gmail.com'
    user.is_authorized = False
    user.save()

    # Store the OTP in the session
    request.session['verification_otp'] = otp
    request.session['verification_email'] = user_email

    # Send the OTP email
    send_mail(
        "Email Verification",
        f"Your OTP for registration is {otp}.",
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
