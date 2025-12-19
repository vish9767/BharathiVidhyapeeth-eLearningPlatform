from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ForgotPasswordSerializer, VerifyOtpSerializer,UserProfileSerializer,CourseSerializer,QuestionsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from .models import User,Course,Topic,Questions
from rest_framework.permissions import IsAuthenticated,IsAdminUser

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

from rest_framework.permissions import AllowAny


class ForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]
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
    




#####################################################course API view#########################################



class CourseCreateAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    @swagger_auto_schema(operation_summary="Create Course",request_body=CourseSerializer)
    def post(self, request):
        with transaction.atomic():
            serializer = CourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({"message": "Course created","data": serializer.data},status=status.HTTP_201_CREATED)

class CourseListAPI(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get Course List",
        operation_description="Retrieve a list of all courses",
        responses={200: CourseSerializer(many=True), 401: "Unauthorized"}
    )
    def get(self, request):
        user_level = request.user.level  # 1 or 2
        courses = Course.objects.filter(is_delete=False).order_by("-created_at")
        serializer = CourseSerializer(courses, many=True)
        return Response({"message": "Courses fetched","data": serializer.data})
    

class CourseDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get Course Detail",
        operation_description="Retrieve a specific course by ID",
        responses={200: CourseSerializer, 401: "Unauthorized"}
    )
    def get(self, request, c_id):
        course = Course.objects.get(c_id=c_id, is_delete=False)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
class CourseDeleteAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    @swagger_auto_schema(
        operation_summary="Delete Course",
        operation_description="Delete a specific course by ID",
        responses={200: "Course deleted successfully", 401: "Unauthorized"})
    def delete(self, request, c_id):
        course = Course.objects.get(c_id=c_id)
        course.is_delete = True
        course.save()
        return Response({"message": "Course deleted"})
    

from .models import Media
from .serializers import MediaSerializer
from rest_framework import status, permissions
from .serializers import TopicSerializer

class MediaListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get all media or media by topic_id
        """
        topic_id = request.query_params.get('topic_id')

        media_qs = Media.objects.filter(is_delete=False)

        if topic_id:
            media_qs = media_qs.filter(topic_id=topic_id)

        serializer = MediaSerializer(
            media_qs,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)





class CourseTopicsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        """
        Get all topics for a given course ID
        """
        try:
            course = Course.objects.get(c_id=course_id, is_delete=False)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        topics = Topic.objects.filter(
            course=course,
            is_delete=False
        ).prefetch_related('media')

        serializer = TopicSerializer(
            topics,
            many=True,
            context={'request': request}
        )

        questions = Questions.objects.filter(topic__course=course)
        questions_serializer = QuestionsSerializer(questions, many=True)
        return Response(
            {
                "course_id": course.c_id,
                "course_title": course.title,
                "topics": serializer.data,
                "questions": questions_serializer.data,
            },
            status=status.HTTP_200_OK
        )