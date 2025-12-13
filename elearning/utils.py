from django.contrib.auth.hashers import make_password, check_password

def hash_password(password):
    return make_password(password)

def verify_password(password, hashed_password):
    return check_password(password, hashed_password)





import random
from django.utils import timezone
from datetime import timedelta

def generate_otp():
    return str(random.randint(100000, 999999))

def is_otp_valid(user):
    if not user.otp or not user.otp_created_at:
        return False
    return timezone.now() <= user.otp_created_at + timedelta(minutes=10)
