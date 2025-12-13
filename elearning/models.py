from django.db import models
from django_enumfield import enum


class UserLevel_enum(enum.Enum):
    Level_1=1
    Level_2=2
    __default__= 2

class User(models.Model):
    u_id = models.AutoField(primary_key=True)   
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    level = enum.EnumField(UserLevel_enum)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.email
