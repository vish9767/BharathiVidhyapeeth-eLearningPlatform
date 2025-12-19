from django.contrib import admin
from .models import User,Course,Media,Topic,Questions
# Register your models here.
admin.site.site_header = "CAI Elearning Admin"
admin.site.site_title = "CAI Elearning Admin Portal"
admin.site.index_title = "Welcome to CAI Elearning Admin Portal"
# admin.site.unregister(User)  # Unregister the default User admin
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Media)
admin.site.register(Topic)
admin.site.register(Questions)


