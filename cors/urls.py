from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
urlpatterns = [

    # TOKEN JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # register & login-1 & login-2 & logout
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path("login/send_otp/", views.UserOTPLoginView.as_view(), name="send_otp"),
    path("login/verify_otp/", views.UserOTPVerifyView.as_view(), name="verify_otp"),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateUserProfileView.as_view(), name='profile_update'),

    # password_reset & password_confirm & new_password
    path('password_reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('set_new_password/', views.SetNewPasswordView.as_view(), name='set_new_password'),


]