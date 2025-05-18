from rest_framework import serializers
from .models import CustomUser, OTP
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()