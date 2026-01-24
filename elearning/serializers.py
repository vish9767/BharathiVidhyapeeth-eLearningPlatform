from rest_framework import serializers
from .models import User,Course,Topic,Questions,UserCourseProgress
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



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

from .utils import generate_otp
from django.core.mail import send_mail  # for sending OTP via email

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            print("Validating email: ", value)
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
        print(f"OTP for {email} is {otp}")
        # send OTP via email (example)
        send_mail(
            subject='Your OTP for Password Reset',
            message=f'Your OTP is {otp}. It will expire in 10 minutes.',
            from_email='noreply@example.com',
            recipient_list=[email],)
        return user


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
    comp_status = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ("c_id","title","description","created_at","comp_status")
    def get_comp_status(self, course):
        user = self.context["request"].user
        try:
            progress = UserCourseProgress.objects.get(
                user=user,
                course=course
            )
        except UserCourseProgress.DoesNotExist:
            return False
        total_topics = Topic.objects.filter(
            course=course,
            is_delete=False
        ).count()
        completed_topics = progress.completed_topics.count()
        if total_topics == 0:
            return False
        return completed_topics == total_topics

########################################course Serializer#########################################
from rest_framework import serializers
from .models import Media

class MediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = [
            'm_id',
            'media_type',
            'file_url',
            'caption',
            'created_at'
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url
    



class TopicSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = [
            't_id',
            'title',
            'description',
            'media',
            'created_at'
        ]

class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['q_id','question_text','option_a','option_b','option_c','option_d']



from rest_framework import serializers

class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'])


class SubmitTestSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    topic_id = serializers.IntegerField()
    answers = AnswerItemSerializer(many=True)