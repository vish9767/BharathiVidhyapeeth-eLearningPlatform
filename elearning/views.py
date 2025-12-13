from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ForgotPasswordSerializer, VerifyOtpSerializer,UserProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

# from .jwt import MyJWTAuthentication  # our custom class


from .jwt import generate_jwt


from django.db import connection



class HealthCheckAPIView(APIView):
    authentication_classes = []
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            connection.ensure_connection()
            return Response({"status": "ok","service": "CAI Backend","database": "connected"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error","service": "CAI Backend","database": "disconnected","error": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)







class RegisterAPI(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_summary="User Registration",
        operation_description="Register a new user and return JWT tokens",
        request_body=RegisterSerializer,
        responses={201: openapi.Response("User registered successfully"),400: "Bad Request",},)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = generate_jwt(user)
        return Response({"message": "Registration successful","user_id": user.u_id,**tokens},status=status.HTTP_201_CREATED)


class LoginAPI(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Login a user and return JWT tokens",
        request_body=LoginSerializer,
        responses={200: openapi.Response("User logged in successfully"),400: "Bad Request",},)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = generate_jwt(user)
        return Response({"message": "Login successful","user_id": user.u_id,**tokens}, status=status.HTTP_200_OK)



class ForgotPasswordAPI(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_summary="Forgot Password",
        operation_description="Send OTP to user's email for password reset",
        request_body=ForgotPasswordSerializer,
        responses={200: openapi.Response("OTP sent to your email"),400: "Bad Request",},)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOtpAPI(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_summary="Verify OTP",
        operation_description="Verify OTP and reset user's password",
        request_body=VerifyOtpSerializer,
        responses={200: openapi.Response("Password reset successfully"),400: "Bad Request",},)
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)




from rest_framework_simplejwt.authentication import JWTAuthentication

class userProfileAPI(APIView):
    authentication_classes = [JWTAuthentication]  # Use SimpleJWT
    permission_classes = [IsAuthenticated] 
    @swagger_auto_schema(
        operation_summary="Get User Profile",
        operation_description="Retrieve authenticated user's profile details",
        responses={200: UserProfileSerializer, 401: "Unauthorized"}
    )
    def get(self, request):
        # user_id = request.user['user_id']
        print("this is request user found ",request)
        # print("this is request data found ",request)
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update User Profile",
        operation_description="Update authenticated user's profile",
        request_body=UserProfileSerializer,
        responses={200: "Profile updated successfully", 400: "Bad Request", 401: "Unauthorized"}
    )
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)