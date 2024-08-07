import random
import requests
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.auth.models import update_last_login
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import TimeStamp, ChangeRequest, Video
from .serializators import (
    UserSerializer, TimeStampSerializer, VideoSerializer, 
    UserUpdateSerializer, Response400Serializer, PasswordUpdateSerializer, 
    PasswordUpdateConfirmSerializer, TimeStampPaginateSchema, VideoPaginateSchema, TriggerSerializer
)

class IsAdminUserOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
                or request.method in permissions.SAFE_METHODS)

def generate_verification_code(length=settings.VERIFICATION_CODE_LENGTH):
    digits = "0123456789"
    verification_code = "".join(random.choice(digits) for _ in range(length))
    return verification_code

def send_confirm_code(user, code):
    # Placeholder function to send the confirmation code to the user
    pass

class UserCreateView(APIView):
    @extend_schema(
        request=UserSerializer,
        responses={201: TokenObtainSlidingSerializer, 400: Response400Serializer},
        description='Create a new user'
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            token = SlidingToken.for_user(serializer.instance)
            update_last_login(None, serializer.instance)
            return Response({'token': str(token)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None, 
        responses={200: UserSerializer},
        description='Get user information'
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=UserUpdateSerializer, 
        responses={204: None, 400: Response400Serializer},
        description='Update user information'
    )
    def post(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=PasswordUpdateSerializer, 
        responses={204: None, 400: Response400Serializer},
        description='Update user password'
    )
    def post(self, request):
        user = request.user
        serializer = PasswordUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            confirm_code = generate_verification_code()
            ChangeRequest(user=user, field='password', confirm_code=confirm_code, new_value=serializer.validated_data['password']).save()
            send_confirm_code(user, confirm_code)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateConfirmView(APIView):
    @extend_schema(
        request=PasswordUpdateConfirmSerializer,
        responses={204: None, 400: Response400Serializer},
        description='Confirm user password update'
    )
    def post(self, request):
        confirm_code = request.data.get('confirm_code', None)
        user = request.user
        if not confirm_code:
            return Response({"detail": {'confirm_code': 'field is required'}}, status=status.HTTP_400_BAD_REQUEST)

        ChangeRequest.cleanup_expired_user_change_requests(user, 'password')
        try:
            change_request = ChangeRequest.objects.get(user=user, confirm_code=confirm_code, field='password')
        except ChangeRequest.DoesNotExist:
            return Response({"detail": {'confirm_code': 'invalid or expired'}}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(change_request.new_value)
        user.save()
        change_request.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TimeStampListView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=None, 
        parameters=[OpenApiParameter(name='video_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: TimeStampPaginateSchema(many=True), 400: Response400Serializer},
        description='Get timestamps for a video'
    )
    def get(self, request, video_id):
        try:
            video_id = int(video_id)
        except ValueError:
            return Response({"detail": "Invalid video ID."}, status=status.HTTP_400_BAD_REQUEST)

        timestamps = TimeStamp.objects.filter(video_id=video_id).order_by('created_at')
        results = self.paginate_queryset(timestamps, request, view=self)
        serializer = TimeStampSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)


class TimeStampCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        request=TimeStampSerializer, 
        responses={201: None, 400: Response400Serializer},
        description='Create a new timestamp',
         examples=[
            OpenApiExample(
                "Valid Request Example",
                value={
                    "video": 1,
                    "aroma": "A",
                    "moment": "10:30:45"
                }
            )
        ]
    )
    def post(self, request):
        
        serializer = TimeStampSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoListView(APIView, PageNumberPagination):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsAdminUserOrReadOnly]

    @extend_schema(
        request=None, 
        responses={200: VideoPaginateSchema(many=True), 400: Response400Serializer},
        description='Get all videos'
    )
    def get(self, request):
        videos = Video.objects.order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    
    @extend_schema(
        request=VideoSerializer, 
        responses={201: None, 400: Response400Serializer},
        description='Create a new video'
    )
    
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=None, 
        parameters=[OpenApiParameter(name='video_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: VideoSerializer, 400: Response400Serializer},
        description='Get video detail'
    )
    def get(self, request, video_id):
        try:
            video_id = int(video_id)
        except ValueError:
            return Response({"detail": {'video': "Invalid ID."}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"detail": {'video': "not found"}}, status=status.HTTP_404_NOT_FOUND)

        video.views += 1
        video.save()
        serializer = VideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularVideoListView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=None, 
        responses={200: VideoPaginateSchema(many=True), 400: Response400Serializer},
        description='Get popular videos'
    )
    def get(self, request):
        videos = Video.objects.order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)


class SearchVideoListView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        parameters=[OpenApiParameter(name='query', description='Search video list', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY)],
        request=None, 
        responses={200: VideoPaginateSchema(many=True), 400: Response400Serializer},
        description='Search videos'
    )
    def get(self, request):
        query = request.query_params.get('query', None)
        if not query:
            return Response({"detail": {'query': "field is required."}}, status=status.HTTP_400_BAD_REQUEST)

        search_vector = SearchVector('title', 'description')
        search_query = SearchQuery(query)
        videos = Video.objects.annotate(search=search_vector).filter(search=search_query).order_by('-views')
        results = self.paginate_queryset(videos, request, view=self)
        serializer = VideoSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)


class TriggerListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TriggerSerializer,
        responses={204: None, 400: Response400Serializer},
        description='Activate trigger'
    )
    def post(self, request):
        serializer = TriggerSerializer(data=request.data)
        if serializer.is_valid():
            aroma = serializer.validated_data['timestamp']['aroma']
            arduino_url = settings.ARDUINO_URL.format(aroma)
            response = requests.get(arduino_url)
            if response.status_code == 200:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"error": f"Failed to trigger aroma {aroma}"}, status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
