from django.shortcuts import render
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import *
from rest_framework.permissions import *
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.

class CreateUserView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class Login(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')

        user=authenticate(request,email=email,password=password)
        if user is not None:
            # Generate token for the user
            token, created = Token.objects.get_or_create(user=user)
            # Return user details along with token
            return Response({
                'id':user.id,
                'token': token.key,
                'name': f"{user.first_name} {user.last_name}",
                'role': user.role
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid email and/or password'}, status=status.HTTP_401_UNAUTHORIZED) 


class Logout(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        token=Token.objects.get(user=request.user)
        token.delete()
        return Response({'message':'logged out successfully'},status=status.HTTP_200_OK)


class UserDetailsView(RetrieveAPIView):
    serializer_class=UserSerializer
    lookup_field='pk'
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        user=self.request.user
        user_id=self.kwargs.get('pk')

        if user.role=='admin':
            return User.objects.all()
        return User.objects.filter(id=user_id)

class UpdateProfile(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class=UserSerializer
    def patch(self, request,):
        user = self.request.user

        last_name = request.data.get('last_name')
        first_name = request.data.get('first_name')
        email = request.data.get('email')
        job_role = request.data.get('job_role')
        phone_number = request.data.get('phone_number')
        salary = request.data.get('salary')
        department=request.data.get('department')


        if user.role == "admin":
            if job_role is not None:
                user.job_role = job_role
            if salary is not None:
                user.salary = salary
            if department is not None:
                user.department = department
        else:
            (Response({"Error:You are unauthorised"},status=status.HTTP_401_UNAUTHORIZED))
        if last_name is not None:
            user.last_name = last_name
        if first_name is not None:
            user.first_name = first_name
        if phone_number is not None:
            user.phone_number = phone_number

        # Save the updated user
        user.save()

        # Return a success response
        return Response({
            "message": "Profile updated successfully",
        }, status=status.HTTP_200_OK)  

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password length (the confirmation will be done in frontend)
        if len(new_password) < 8:
            return Response(
                {"error": "New password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set and save the new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK
        )   

