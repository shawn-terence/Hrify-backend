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
