from sre_parse import State
from rest_framework import serializers
from .models import  FriendRequest, Userkap
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=80)
    username = serializers.CharField(max_length=45)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Userkap
        fields = ["email", "username", "password","first_name", "last_name"]
    
    def validate(self, attrs):

        email_exists = Userkap.objects.filter(email=attrs["email"]).exists()

        if email_exists:
            raise ValidationError("Email has already been used")

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = super().create(validated_data)

        user.set_password(password)

        user.save()

        Token.objects.create(user=user)

        return user

class UserkapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userkap
        fields = ["email", "username","first_name", "last_name"]
    
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
    

