"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import ( UserSignUpView, UserLoginView, UserView,
                     GetVideosView, UploadVideoView, GetUsersView,
                     VerifyOtpView, ResendOtpView, VideoView, 
                     UpdateSubscriptionView, DeleteUserView
                    )        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup_view'),
    path('login/', UserLoginView.as_view(), name='login_view'),
    # path('logout/', logout_view, name='logout_view'),
    # path('check-auth/', check_auth_view, name='check_auth_view'),
    path('update-user/', UserView.as_view(), name='update_user'),
    path('upload-video/', UploadVideoView.as_view(), name='upload_video'),
    path('delete-video/<str:video_id>/', VideoView.as_view(), name='delete-video'),
    path('get-video/<str:video_id>/', VideoView.as_view(), name='get-video'),
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('forget/', reset_password, name='reset-password'),

    path('get-videos/', GetVideosView.as_view(), name='get-videos'),
    path('get-users/', GetUsersView.as_view(), name='get-users'),
    path('get-user/', UserView.as_view(), name='get-users'),
    path('otp/', VerifyOtpView.as_view(), name='otp'),
    path('resend_otp/', ResendOtpView.as_view(), name='resend-otp'),
    path('update_subscription/', UpdateSubscriptionView.as_view(), name='update-subscription'),
    
    path('delete-user/<str:email>/', DeleteUserView.as_view(), name='delete-user'),

]