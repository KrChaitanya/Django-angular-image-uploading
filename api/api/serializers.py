# user_management/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'user', 'image','title','description','grid_position','upload_date']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name','first_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}
