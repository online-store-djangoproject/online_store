from django.shortcuts import render
from rest_framework.generics import GenericAPIView,UpdateAPIView
from rest_framework.views import APIView
from rest_framework import status
from django.views import View
from rest_framework.response import Response
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserOTPLoginSerializer, UserOTPVerifySerializer, \
    LogoutUserSerializer, SetNewPasswordSerializer, PasswordResetRequestSerializer, UserProfileSerializer
from .models import User
from permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Create your views here.


class UserRegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                user = serializer.instance
                print(user)
                return Response({
                    'data': UserRegisterSerializer(user).data,
                    'message': f'Hi {user.get_full_name()}! Thanks for signing up.'
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login method 1

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({
                "data": serializer.validated_data,
                "message": "Login successful."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login method 2

class UserOTPLoginView(APIView):
    def post(self, request):
        serializer = UserOTPLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({
                "message": "OTP has been sent to your email."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOTPVerifyView(APIView):
    def post(self, request):
        serializer = UserOTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({
                "data": serializer.validated_data,
                "message": "Login successful."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# === PassWord ===

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'a link has been sent to your email to reset your password'}, status=status.HTTP_200_OK)


class PasswordResetConfirm(GenericAPIView):
    def get(self, request,uidb64, token):
        try:
            print(f"Received uidb64: {uidb64}")
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            print(f"Decoded User ID: {user_id}")
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True,'message':'credentials is valid','uidb64':uidb64,'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message':'password reset successfull'},status=status.HTTP_200_OK)


#  ===LogOut===

class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

#  profile update (firstname & lastname)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly,]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly,]

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)