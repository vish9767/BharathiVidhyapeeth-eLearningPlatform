from django.db import models
from django_enumfield import enum
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError

class UserLevel_enum(enum.Enum):
    Level_1 = 1
    Level_2 = 2
    __default__ = 2

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    u_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    level = enum.EnumField(UserLevel_enum)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # required for admin
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'       # login with email
    REQUIRED_FIELDS = ['first_name', 'last_name']  # required when creating superuser

    def __str__(self):
        return self.email




class Course(models.Model):
    c_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='media/', blank=True, null=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    



class Topic(models.Model):
    t_id = models.AutoField(primary_key=True)
    course = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='modules')
    description = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Media(models.Model):
    m_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=20,choices=[('video', 'Video'),('image', 'Image'),('animation', 'Animation'),('document', 'Word File'),])
    file = models.FileField(upload_to='media/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def clean(self):
            # If video type → require video_url, not file
            if self.media_type == 'video':
                if not self.video_url:
                    raise ValidationError("Video URL is required for video type.")
                if self.file:
                    raise ValidationError("Do not upload file when media type is video.")
            # If not video → require file, not video_url
            else:
                if not self.file:
                    raise ValidationError("File is required for non-video media types.")
                if self.video_url:
                    raise ValidationError("Video URL should only be used for video type.")
    def __str__(self):
        return f"{self.topic.title} - {self.media_type}"
        


class Questions(models.Model):
    q_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='questions')
    que_type=models.CharField(max_length=20,choices=[('mcq', 'Mcq'),('pair', 'Pair'),('imgage', 'Image')])
    question_text = models.TextField()
    option_a = models.CharField(max_length=255,blank=True, null=True)
    option_b = models.CharField(max_length=255,blank=True, null=True)
    option_c = models.CharField(max_length=255,blank=True, null=True)
    option_d = models.CharField(max_length=255,blank=True, null=True)
    file = models.FileField(upload_to='media/', blank=True, null=True)
    correct_option = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Question {self.q_id} for Topic {self.topic.title}"
    

    
class UserAnswer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('elearning.User',on_delete=models.CASCADE,related_name='answers')
    question = models.ForeignKey('Questions',on_delete=models.CASCADE,related_name='user_answers')
    selected_option = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.email} - Q{self.question.q_id}"
    
class UserCourseProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('elearning.User',on_delete=models.CASCADE,related_name='course_progress')
    course = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='user_progress')
    completed_topics = models.ManyToManyField('Topic',blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"