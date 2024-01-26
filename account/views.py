from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.conf import settings
from rest_framework.authtoken.models import Token

from account.utils import Util
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'mobile', 'batch_year', 'branch', 'gender', 'image']
    


 
class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'role', 'gender', 'branch', 'mobile', 'batch_year', 'image']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        try:
            email = validated_data['email']
            role = validated_data['role']
        except KeyError:
            raise serializers.ValidationError({'error': 'Email and role are required.'})
        
        
        
        if role == CustomUser.USER_ROLES.ADMIN:
            raise serializers.ValidationError({'role': 'Invalid role'})
        
        if role == CustomUser.USER_ROLES.STUDENT:

            # Check if the email domain is meaec.edu.in
            if not email.endswith('@meaec.edu.in'):
                raise serializers.ValidationError({'email': 'Invalid email domain'})

            try:
                batch_year = int(email[:2])
            except ValueError:
                raise serializers.ValidationError({'email': 'Invalid email'})

            user = CustomUser.objects.create(
                batch_year=batch_year,
                is_active=False,
                **validated_data
            )
            user.set_password(validated_data['password'])
            user.save()
            send_otp_email(email)
        
        if role == CustomUser.USER_ROLES.JUDGE:
            user = CustomUser.objects.create(
                is_active=True,
                **validated_data
            )
            user.set_password(validated_data['password'])
            user.save()

        
        
        return user
        
        


def send_otp_email(email):
    user = CustomUser.objects.get(email=email)
    user.otp = Util.generateOTP()
    user.save()
    
    email_body = f'Hi {user.first_name},\n\nYour OTP is {user.otp}.\n\nRegards,\nEventrave Team'
    data = {
        'subject': 'Eventrave Registration OTP',
        'body': email_body,
        'to_email': user.email
    }
    Util.send_email(data)



class CustomUserRegistrationView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data['email'] if 'email' in request.data else None
        role = request.data['role'] if 'role' in request.data else None
        if email and CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': 'Email already exists'})
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)   
        serializer.save()

        if role == CustomUser.USER_ROLES.STUDENT:
            return Response({'message': 'CustomUser registered successfully. Check your email for otp.'},
                        status=status.HTTP_201_CREATED, )
        return Response({'message': 'User registered successfully.'},
                        status=status.HTTP_201_CREATED, )


class CustomUserAccountActivationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        otp = request.data.get('otp', None)
        print(email,otp)
        

        if not email or not otp:
            return Response({'error': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        print(user.otp)
        if not user.is_active:
            if user.otp == otp:
                user.is_active = True
                user.otp = None
                user.save()
                
                #Create a token for the user
                token, created = Token.objects.get_or_create(user=user)
                userData = CustomUserSerializer(user,context={"request":request}).data
                
                return Response({**userData,"token":token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User is already active.'}, status=status.HTTP_400_BAD_REQUEST)
        



class CustomUserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_active:
            send_otp_email(email)
            return Response({'error': 'User is not active. Check your email for otp.'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        
        if user.check_password(password):
            # Delete existing tokens for the user
            Token.objects.filter(user=user).delete()

            # Create a new token
            token, created = Token.objects.get_or_create(user=user)
            user_data = CustomUserSerializer(user,context={"request":request}).data

            return Response({**user_data, 'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)






class CustomUserProfileView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            user_data = CustomUserSerializer(user,context={"request":request}).data
            token, created = Token.objects.get_or_create(user=user)
            return Response({**user_data,"token":token.key}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, *args, **kwargs):
        user = request.user
        user_data = CustomUserSerializer(user, data=request.data, partial=True,context={"request":request})
        user_data.is_valid(raise_exception=True)
        user_data.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({**user_data.data,"token":token.key}, status=status.HTTP_200_OK)