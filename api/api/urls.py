from django.urls import path
from .views import RegisterView, LoginView, UserDetail, ImagesView, ImageView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/<str:id>/', UserDetail.as_view(), name='user_detail'),
    path('users/<str:id>/images/', ImagesView.as_view(), name='images'),
    path('users/<str:user_id>/images/<str:grid_position>/', ImageView.as_view(), name='image'),
]