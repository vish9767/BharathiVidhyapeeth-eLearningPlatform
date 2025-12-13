from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ForgotPasswordSerializer, VerifyOtpSerializer

from .jwt import generate_jwt

class RegisterAPI(APIView):
    permission_classes = []
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = generate_jwt(user)
        return Response({
            "message": "Registration successful",
            "user_id": user.u_id,
            **tokens
        }, status=status.HTTP_201_CREATED)


class LoginAPI(APIView):
    permission_classes = []
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = generate_jwt(user)
        return Response({
            "message": "Login successful",
            "user_id": user.u_id,
            **tokens
        }, status=status.HTTP_200_OK)



class ForgotPasswordAPI(APIView):
    permission_classes = []
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOtpAPI(APIView):
    permission_classes = []
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
