from django.urls import path
from .views import RegisterAPI, LoginAPI, ForgotPasswordAPI, VerifyOtpAPI, HealthCheckAPIView,userProfileAPI

urlpatterns = [
    path("health/", HealthCheckAPIView.as_view(), name="health-check"),
    path('register/', RegisterAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('forgot-password/', ForgotPasswordAPI.as_view()),
    path('verify-otp/', VerifyOtpAPI.as_view()),
    path('profile/', userProfileAPI.as_view()), #name='user-profile'),


]
