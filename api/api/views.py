from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Image
from .serializers import ImageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.cache import cache

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.save()

            refresh_token = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh_token),
                'access': str(refresh_token.access_token)
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = RefreshToken.for_user(user)
        response_data = {
            'user': UserSerializer(user).data,
            'access': str(refresh_token.access_token),
        }
        return Response(response_data, status=status.HTTP_200_OK)



class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return User.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def get(self, request, id):
        cache_key = f'user_{id}'
        user = cache.get(cache_key)
        if not user:
            user = self.get_object(id)
            if user is None:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            cache.set(cache_key, user)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ImagesView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    MAX_GRID_SIZE = 16

    def post(self, request, id):
        cache_key = f'user_images_{id}'
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        grid_position = request.data.get('grid_position', None)
        if grid_position is None or int(grid_position) < 0 or int(grid_position) >= self.MAX_GRID_SIZE:
            return Response({'detail': 'Invalid grid position.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            existing_image = Image.objects.get(user=user, grid_position=grid_position)
            existing_image.delete()
        except ObjectDoesNotExist:
            pass

        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            cache.delete(cache_key)
            serializer.save(user=user, grid_position=grid_position)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        cache_key = f'user_images_{id}'
        images = cache.get(cache_key)
        if not images:
            try:
                user = User.objects.get(id=id)
            except ObjectDoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            try:
                user = User.objects.get(id=id)
            except ObjectDoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            try:
                images = Image.objects.filter(user=user)
            except ObjectDoesNotExist:
                return Response({'detail': 'Images not found.'}, status=status.HTTP_404_NOT_FOUND)
            cache.set(cache_key, images)

        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ImageView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, user_id, grid_position):
        try:
            user = User.objects.get(id=user_id)
            return Image.objects.get(user=user, grid_position=grid_position)
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_id, grid_position):
        image_obj = self.get_object(user_id, grid_position)
        if image_obj is None:
            raise Http404("Image not found")

        image_path = os.path.join(settings.MEDIA_ROOT, str(image_obj.image))
        response = FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
        return response

    def delete(self, request, user_id, grid_position):
        cache_key = f'user_images_{user_id}'
        image_obj = self.get_object(user_id, grid_position)
        if image_obj is None:
            raise Http404("Image not found")

        image_path = os.path.join(settings.MEDIA_ROOT, str(image_obj.image))
        if os.path.exists(image_path):
            default_storage.delete(str(image_obj.image))

        image_obj.delete()
        cache.delete(cache_key)
        return Response({'detail': 'Image deleted.'}, status=status.HTTP_204_NO_CONTENT)
