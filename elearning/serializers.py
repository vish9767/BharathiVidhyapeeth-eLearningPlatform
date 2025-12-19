from rest_framework import serializers
from .models import User,Course,Module
from django.db import transaction
from .utils import hash_password, verify_password
from django.utils import timezone
from datetime import timedelta

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'mobile', 'level', 'password')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                validated_data['password'] = hash_password(validated_data['password'])
                user = User.objects.create(**validated_data)
                return user
        except Exception:
            raise serializers.ValidationError("Registration failed. Please try again.")
        # validated_data['password'] = hash_password(validated_data['password'])
        # return User.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'], is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not verify_password(data['password'], user.password):
            raise serializers.ValidationError("Invalid credentials")

        return user




from .utils import generate_otp
from django.core.mail import send_mail  # for sending OTP via email

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not registered")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # send OTP via email (example)
        try:
            send_mail(
                subject='Your OTP for Password Reset',
                message=f'Your OTP is {otp}. It will expire in 10 minutes.',
                from_email='noreply@example.com',
                recipient_list=[email],
            )
            return user
        except Exception as e:
            return {"user":user,'otp':otp}
    

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email")

        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP")

        from .utils import is_otp_valid
        if not is_otp_valid(user):
            raise serializers.ValidationError("OTP expired")

        return data

    def save(self):
        email = self.validated_data['email']
        otp = self.validated_data['otp']
        new_password = self.validated_data['new_password']

        from django.contrib.auth.hashers import make_password
        user = User.objects.get(email=email)
        user.password = make_password(new_password)
        user.otp = None
        user.otp_created_at = None
        user.save()
        return user




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Include fields you want to expose
        fields = ('u_id', 'first_name', 'last_name', 'email', 'mobile', 'level', 'created_at')
        read_only_fields = ('u_id', 'email', 'created_at')  # make some fields read-only






########################################course Serializer#########################################




class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "c_id",
            "title",
            "description",
            "created_at",
        )
