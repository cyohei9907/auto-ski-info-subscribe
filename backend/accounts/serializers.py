from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("パスワードが一致しません")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()  # メールアドレスまたはユーザー名を受け付ける
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email')
        password = attrs.get('password')

        if email_or_username and password:
            # まずメールアドレスとして認証を試みる
            user = authenticate(username=email_or_username, password=password)
            
            # 失敗した場合、ユーザー名として認証を試みる
            if not user:
                try:
                    user_obj = User.objects.get(username=email_or_username)
                    user = authenticate(username=user_obj.email, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('無効な認証情報です')
            if not user.is_active:
                raise serializers.ValidationError('ユーザーアカウントが無効です')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('メールアドレス/ユーザー名とパスワードが必要です')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('user_email', 'avatar', 'timezone', 'notification_enabled')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_premium', 'created_at', 'profile')