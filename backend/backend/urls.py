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
from .views import ( UserSignUpView, UserLoginView, UpdateUserView, GetUserView,
                     GetVideosView, GetAllVideosView, UploadVideoView, GetUsersView, AddSubjectToFacultyMemberView,
                     VerifyOtpView, ResendOtpView, VideoView, GetFacultyMembersView, CreateFacultyMemberView,
                     UpdateSubscriptionView, DeleteUserView, RequestSubscriptionView, DeleteFacultyMemberView, DeleteSubjectOfFacultyMemberView,
                     CheckSubscriptionView, GetAllRequestsView, GetLoggedInFacultyMemberView
                    )        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup_view'),
    path('login/', UserLoginView.as_view(), name='login_view'),
    path('update-user/', UpdateUserView.as_view(), name='update_user'),
    path('upload-video/', UploadVideoView.as_view(), name='upload_video'),
    path('delete-video/<str:video_id>/', VideoView.as_view(), name='delete-video'),
    path('get-video/<str:video_id>/', VideoView.as_view(), name='get-video'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-videos/', GetVideosView.as_view(), name='get-videos'),
    path('get-all-videos/', GetAllVideosView.as_view(), name='get-videos'),
    path('get-users/', GetUsersView.as_view(), name='get-users'),
    path('get-user/', GetUserView.as_view(), name='get-user'),
    path('otp/', VerifyOtpView.as_view(), name='otp'),
    path('resend_otp/', ResendOtpView.as_view(), name='resend-otp'),
    path('update_subscription/', UpdateSubscriptionView.as_view(), name='update-subscription'),
    path('delete-user/<str:email>/', DeleteUserView.as_view(), name='delete-user'),
    path('request-subscription/', RequestSubscriptionView.as_view(), name='request-subscription'),
    path('check-subscription/', CheckSubscriptionView.as_view(), name='check-subscription'),
    path('get-all-requests/', GetAllRequestsView.as_view(), name='get-all-requests'),
    path('get-faculty-members/', GetFacultyMembersView.as_view(), name='get-faculty-members'),
    path('delete-faculty-member/<str:email>/', DeleteFacultyMemberView.as_view(), name='delete-faculty-member'),
    path('create-faculty-member/', CreateFacultyMemberView.as_view(), name='create-faculty-member'),
    path('create-faculty-member-subject/', AddSubjectToFacultyMemberView.as_view(), name='create-faculty-member-subject'),
    path('delete-faculty-member-subject/', DeleteSubjectOfFacultyMemberView.as_view(), name='delete-faculty-member-subject'),
    path('get-faculty-member/', GetLoggedInFacultyMemberView.as_view(), name='get-faculty-member'),
]