from django.db import models
from django_enumfield import enum
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

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
    file = models.FileField(upload_to='media/')
    caption = models.CharField(max_length=255, blank=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.topic.title + " - " + self.media_type
    


class Questions(models.Model):
    q_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Question {self.q_id} for Topic {self.topic.title}"
    
    
    

