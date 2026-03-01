from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ForgotPasswordSerializer,LogoutSerializer, VerifyOtpSerializer,UserProfileSerializer,CourseSerializer,QuestionsSerializer,SubmitTestSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from .models import User,Course,Topic,Questions,UserCourseProgress,UserAnswer
from rest_framework.permissions import IsAuthenticated,IsAdminUser

# from .jwt import MyJWTAuthentication  # our custom class


from .jwt import generate_jwt
from django.db import connection


def home_html(request):
    return render(request, "home.html")


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
    @swagger_auto_schema(operation_summary="User Registration",operation_description="Register a new user and return JWT tokens",request_body=RegisterSerializer,responses={201: openapi.Response("User registered successfully"),400: "Bad Request",},)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = generate_jwt(user)
        return Response({"message": "Registration successful","user_id": user.u_id,**tokens},status=status.HTTP_201_CREATED)

class LoginAPI(APIView):
    permission_classes = []
    @swagger_auto_schema(operation_summary="User Login",operation_description="Login a user and return JWT tokens",request_body=LoginSerializer,responses={200: openapi.Response("User logged in successfully"),400: "Bad Request",},)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = generate_jwt(user)
        return Response({"message": "Login successful","user_id": user.u_id,**tokens}, status=status.HTTP_200_OK)
    

from rest_framework_simplejwt.tokens import RefreshToken



class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_summary="User Logout",operation_description="Logout user by blacklisting refresh token",request_body=LogoutSerializer,responses={200: openapi.Response("User logged out successfully"),400: "Bad Request",401: "Unauthorized",})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"},status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid or expired refresh token"},status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import AllowAny
class ForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(operation_summary="Forgot Password",operation_description="Send OTP to user's email for password reset",request_body=ForgotPasswordSerializer,responses={200: openapi.Response("OTP sent to your email"),400: "Bad Request",},)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOtpAPI(APIView):
    permission_classes = []
    @swagger_auto_schema(operation_summary="Verify OTP",operation_description="Verify OTP and reset user's password",request_body=VerifyOtpSerializer,responses={200: openapi.Response("Password reset successfully"),400: "Bad Request",},)
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)




from rest_framework_simplejwt.authentication import JWTAuthentication
class userProfileAPI(APIView):
    authentication_classes = [JWTAuthentication]  # Use SimpleJWT
    permission_classes = [IsAuthenticated] 
    @swagger_auto_schema(operation_summary="Get User Profile",operation_description="Retrieve authenticated user's profile details",responses={200: UserProfileSerializer, 401: "Unauthorized"})
    def get(self, request):
        # user_id = request.user['user_id']
        print("this is request user found ",request)
        # print("this is request data found ",request)
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Update User Profile",operation_description="Update authenticated user's profile",request_body=UserProfileSerializer,responses={200: "Profile updated successfully", 400: "Bad Request", 401: "Unauthorized"})
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
    @swagger_auto_schema(operation_summary="Get Course List",operation_description="Retrieve all courses with completion status",responses={200: CourseSerializer(many=True), 401: "Unauthorized"})
    def get(self, request):
        courses = Course.objects.filter(is_delete=False).order_by("-created_at")
        serializer = CourseSerializer(courses,many=True,context={"request": request})
        return Response({"message": "Courses fetched","data": serializer.data})
class CourseDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_summary="Get Course Detail",operation_description="Retrieve a specific course by ID",responses={200: CourseSerializer, 401: "Unauthorized"})
    def get(self, request, c_id):
        course = Course.objects.get(c_id=c_id, is_delete=False)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
class CourseDeleteAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    @swagger_auto_schema(operation_summary="Delete Course",operation_description="Delete a specific course by ID",responses={200: "Course deleted successfully", 401: "Unauthorized"})
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
        serializer = MediaSerializer(media_qs,many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)





# class CourseTopicsAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     def get(self, request, course_id):
#         """
#         Get all topics for a given course ID
#         """
#         try:
#             course = Course.objects.get(c_id=course_id, is_delete=False)
#         except Course.DoesNotExist:
#             return Response({"detail": "Course not found"},status=status.HTTP_404_NOT_FOUND)
#         topics = Topic.objects.filter(course=course,is_delete=False).prefetch_related('media')
#         serializer = TopicSerializer(topics,many=True,context={'request': request})
#         questions = Questions.objects.filter(topic__course=course)
#         questions_serializer = QuestionsSerializer(questions, many=True)
#         return Response({"course_id": course.c_id,"course_title": course.title,"topics": serializer.data,"questions": questions_serializer.data,},status=status.HTTP_200_OK)

class CourseTopicsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """x`
        Get all topics for a given course ID with related media
        """
        try:
            course_id = request.data.get('c_id')
            course = Course.objects.get(c_id=course_id, is_delete=False)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        topics = Topic.objects.filter(course=course, is_delete=False).prefetch_related('media')
        serializer = TopicSerializer(topics, many=True, context={'request': request})
        return Response({"course_id": course.c_id,"course_title": course.title,"topics": serializer.data,}, status=status.HTTP_200_OK)


class TopicsQuestionsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        topic_id = request.data.get('t_id')
        # questions = Questions.objects.filter(topic__course=course)
        questions = Questions.objects.filter(topic=topic_id)
        questions_serializer = QuestionsSerializer(questions, many=True)
        return Response({"questions": questions_serializer.data,}, status=status.HTTP_200_OK)

# class SubmitTestAPI(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = SubmitTestSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = request.user
#         course_id = int(serializer.validated_data['chapter_id'])
#         topic_id = int(serializer.validated_data['topic_id'])
#         answers = serializer.validated_data['answers']
#         try:
#             course = Course.objects.get(c_id=course_id, is_delete=False)
#             topic = Topic.objects.get(id=topic_id, course=course)
#         except (Course.DoesNotExist, Topic.DoesNotExist):
#             return Response({"error": "Invalid course or topic"},status=status.HTTP_400_BAD_REQUEST)
#         correct_count = 0
#         with transaction.atomic():
#             for ans in answers:
#                 question = Questions.objects.get(q_id=int(ans['q_id']), topic=topic)
#                 is_correct = question.correct_option.strip().lower() == ans['answer'].strip().lower()#a.strip().lower()
#                 if is_correct:
#                     correct_count += 1
#                 UserAnswer.objects.create(user=user,question=question,selected_option=ans['answer'],is_correct=is_correct)
#             # update or create progress
#             progress, _ = UserCourseProgress.objects.get_or_create(user=user,course=course)
#             progress.completed_topics.add(topic)
#         total_questions = len(answers)
#         score_percentage = round((correct_count / total_questions) * 100, 2)
#         return Response({"message": "Test submitted successfully","total_questions": total_questions,"correct_answers": correct_count,"wrong_answers": total_questions - correct_count,"score_percentage": score_percentage}, status=status.HTTP_201_CREATED)
    

class SubmitTestAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def normalize(self, text):
        if not text:
            return ""
        return " ".join(text.strip().lower().split())

    def post(self, request):
        serializer = SubmitTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        topic_id = int(serializer.validated_data['topic_id'])
        answers = serializer.validated_data['answers']   # ✅ FIXED
        # print("this is answer",answers)
        # validate course + topic
        try:
            topic = Topic.objects.get(t_id=topic_id)
            course=topic.course
        except (Course.DoesNotExist, Topic.DoesNotExist):
            return Response({"error": "Invalid course or topic"},status=status.HTTP_400_BAD_REQUEST)
        correct_count = 0
        with transaction.atomic():
            for ans in answers:
                try:
                    question = Questions.objects.get(q_id=int(ans.get('q_id', 0)),topic=topic)
                except Questions.DoesNotExist:
                    continue  # skip invalid question
                user_answer = self.normalize(ans.get('answer', ''))
                correct_answer = self.normalize(question.correct_option)
                is_correct = user_answer == correct_answer
                if is_correct:
                    correct_count += 1
                UserAnswer.objects.create(user=user,question=question,selected_option = ans.get('answer', ''),is_correct=is_correct)
            # progress update
            progress, _ = UserCourseProgress.objects.get_or_create(user=user,course=course)
            progress.completed_topics.add(topic)

        total_questions = len(answers)
        score_percentage = (
            round((correct_count / total_questions) * 100, 2)
            if total_questions > 0 else 0
        )

        return Response({
            "message": "Test submitted successfully",
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "wrong_answers": total_questions - correct_count,
            "score_percentage": score_percentage
        }, status=status.HTTP_201_CREATED)

# result api 



class UserResultSummaryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        total_attempted = UserAnswer.objects.filter(user=user).count()
        correct = UserAnswer.objects.filter(user=user, is_correct=True).count()
        wrong = total_attempted - correct

        percentage = 0
        if total_attempted > 0:
            percentage = round((correct / total_attempted) * 100, 2)

        return Response({
            "total_questions": total_attempted,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "percentage": percentage
        })
    

from django.db.models import Count, Q


# class UserCourseResultAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         results = (
#             UserAnswer.objects
#             .filter(user=user)
#             .values(
#                 "question__topic__course__c_id",
#                 "question__topic__course__title"
#             )
#             .annotate(
#                 total=Count("answer_id"),
#                 correct=Count("answer_id", filter=Q(is_correct=True))
#             )
#         )

#         response = []
#         for r in results:
#             percentage = round((r["correct"] / r["total"]) * 100, 2)
#             response.append({
#                 "course_id": r["question__topic__course__c_id"],
#                 "course_title": r["question__topic__course__title"],
#                 "total_questions": r["total"],
#                 "correct_answers": r["correct"],
#                 "percentage": percentage
#             })

#         return Response(response)




# class UserCourseResultAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         # get user results grouped by chapter
#         result_map = {
#             r["question__topic__chapter_id"]: r
#             for r in (
#                 UserAnswer.objects
#                 .filter(user=user)
#                 .values("question__topic__course_id")
#                 .annotate(
#                     total = Count("answer_id"),
#                     correct = Count("answer_id", filter=Q(is_correct=True))
#                 )
#             )
#         }

#         # fetch ALL chapters
#         chapters = Course.objects.all()

#         response = []

#         for ch in chapters:
#             data = result_map.get(ch.id)

#             if data:
#                 percentage = round((data["correct"] / data["total"]) * 100, 2)
#             else:
#                 percentage = 0

#             response.append({
#                 "chapter_id": ch.id,
#                 "chapter_name": ch.title,
#                 "percentage": percentage
#             })

#         return Response({"chapters": response})


class UserCourseResultAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # results grouped by COURSE
        results = (
            UserAnswer.objects
            .filter(user=user)
            .values("question__topic__course_id")
            .annotate(
                total=Count("answer_id"),
                correct=Count("answer_id", filter=Q(is_correct=True))
            )
        )

        # convert queryset → dictionary map
        result_map = {
            r["question__topic__course_id"]: r
            for r in results
        }

        # fetch all courses
        courses = Course.objects.all()

        response = []

        for course in courses:
            data = result_map.get(course.c_id)  # use your PK field

            if data and data["total"] > 0:
                percentage = round((data["correct"] / data["total"]) * 100, 2)
            else:
                percentage = 0

            response.append({
                "chapter_id": course.c_id,      # keeping your response format
                "chapter_name": course.title,
                "percentage": percentage
            })

        return Response({"chapters": response})
    




class ChapterTestDetailedResultAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        chapter_id =request.data.get('chapter_id')

        if not chapter_id:
            return Response(
                {"error": "chapter_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            chapter = Course.objects.get(c_id=chapter_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Invalid chapter_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        answers = (
            UserAnswer.objects
            .filter(user=user, question__topic__course_id=chapter_id)
            .select_related("question", "question__topic")
        )

        tests = []

        for ans in answers:
            tests.append({
                "topic_id": ans.question.topic.t_id,
                "question": ans.question.question_text,
                "user_answer": ans.selected_option,
                "correct_answer": ans.question.correct_option,
                "status": "Correct" if ans.is_correct else "Wrong"
            })

        return Response({
            "chapter_id": chapter.c_id,
            "chapter_name": chapter.title,
            "tests": tests
        })