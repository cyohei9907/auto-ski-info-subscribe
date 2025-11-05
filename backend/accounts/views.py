from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer
)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class RegisterView(generics.CreateAPIView):
    """ユーザー登録API"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="新規ユーザー登録",
        responses={
            201: openapi.Response(
                description="登録成功",
                schema=UserSerializer()
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # プロフィール作成
        UserProfile.objects.create(user=user)
        
        # トークン作成
        token, created = Token.objects.get_or_create(user=user)
        
        response = Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
        
        return response


@swagger_auto_schema(
    method='post',
    operation_description="ユーザーログイン",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description="ログイン成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def login_view(request):
    """ログインAPI"""
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    token, created = Token.objects.get_or_create(user=user)
    
    response = Response({
        'user': UserSerializer(user).data,
        'token': token.key
    })
    
    return response


@swagger_auto_schema(
    method='post',
    operation_description="ユーザーログアウト",
    responses={200: openapi.Response(description="ログアウト成功")}
)
@api_view(['POST'])
def logout_view(request):
    """ログアウトAPI"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'ログアウトしました'})


class ProfileView(generics.RetrieveUpdateAPIView):
    """ユーザープロフィールAPI"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserDetailView(generics.RetrieveAPIView):
    """ユーザー詳細API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """CSRF Token取得API"""
    return Response({'detail': 'CSRF cookie set'})