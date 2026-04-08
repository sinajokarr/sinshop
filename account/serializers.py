from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'password_confirm')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm') 
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'created_at')