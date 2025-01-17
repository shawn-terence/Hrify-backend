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
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.
class UserRetrievalMixin:
    def get_user(self, user_id):
        return get_object_or_404(User, id=user_id)

# Mixin for admin check
class IsAdminMixin:
    def is_admin(self, user):
        return user.role == 'admin'
class CreateUserView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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
        print(user)
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
        print(request.user)
        token.delete()
        return Response({'message':'logged out successfully'},status=status.HTTP_200_OK)


class UserDetailsView(RetrieveAPIView,IsAdminMixin):
    serializer_class=UserSerializer
    lookup_field='pk'
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        user=self.request.user
        user_id=self.kwargs.get('pk')

        if self.is_admin(user):
            return User.objects.all()
        return User.objects.filter(id=user_id)

class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Allow handling file uploads
    
    def patch(self, request):
        user = request.user

        # Handle profile picture upload
        profile_picture = request.FILES.get('profile_image')
        if profile_picture:
            user.profile_picture = profile_picture

        # Update other fields
        fields_to_update = ['last_name', 'first_name', 'email', 'job_role', 'phone_number', 'salary', 'department']
        for field in fields_to_update:
            if field in request.data:
                setattr(user, field, request.data[field])

        user.save()

        return Response({
            "message": "Profile updated successfully",
            "profile_picture": user.profile_picture.url if user.profile_picture else None,
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

class MakeReportView(CreateAPIView, UserRetrievalMixin, IsAdminMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        admin = request.user
        
        if not self.is_admin(admin):
            return Response({'message': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = self.kwargs.get('user_id')

        user = self.get_user(user_id)

        data = request.data.copy()
        data['employee'] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        email_query = request.query_params.get('email', None)
        
        # If an email query is provided, filter users by email
        if email_query:
            users = User.objects.filter(email__icontains=email_query)
        else:
            users = User.objects.all()
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ReportCategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Get distinct categories from the Report model
        categories = Report.objects.values_list('category', flat=True).distinct()
        
        # Return the categories as a JSON response
        return Response(categories, status=status.HTTP_200_OK)

class UpdateReportView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer
    lookup_field='id'
    def get_queryset(self):
        return Report.objects.all()


class DeleteReportView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field='id'
    def get_queryset(self):
        return Report.objects.all()

class EmployeeReportView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get_queryset(self):
        user = self.request.user
        return Report.objects.filter(employee_id=user.id)

class AdminReportView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.all()

class RequestLeaveView(ListCreateAPIView, IsAdminMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveSerializer

    def get_queryset(self):
        user = self.request.user
        # if self.is_admin(user):
        #     return Leave.objects.all()
        return Leave.objects.filter(employee=user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class RequestActionView(UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = LeaveSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return Leave.objects.all()

    def patch(self, request, *args, **kwargs):
        leave = self.get_object()
        serializer = self.get_serializer(leave, data=request.data, partial=True)

        if serializer.is_valid():
            status_value = serializer.validated_data.get('status')
            if status_value and status_value not in dict(Leave.LEAVE_STATUS):
                return Response({"status": ["Invalid status value."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set handled_by field based on the status
            if status_value == "approved":
                leave.handled_by = self.request.user
            elif status_value == "rejected":
                leave.handled_by = self.request.user
            
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteLeaveRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            leave_request = Leave.objects.get(pk=pk, employee=request.user)
        except Leave.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if leave_request.status != "pending":
            return Response({"detail": "Only pending requests can be deleted."}, status=status.HTTP_400_BAD_REQUEST)
        
        leave_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LeaveListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveSerializer

    def get_queryset(self):
        # Return all leave requests
        return Leave.objects.all()

class TimeInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Automatically use today's date
        today = timezone.now().date()

        # Check if there's an existing attendance record for today
        try:
            attendance = Attendance.objects.get(employee=user, date=today)
            if attendance.time_in is not None:
                return Response({"detail": "Already recorded time in for today."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                now = timezone.now()
                attendance.time_in = now.time()
                attendance.save()
        except Attendance.DoesNotExist:
            now = timezone.now()
            attendance = Attendance(employee=user, date=today, time_in=now.time())
            attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TimeOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Automatically use today's date
        today = timezone.now().date()

        # Check if there's an existing attendance record for today
        try:
            attendance = Attendance.objects.get(employee=user, date=today)
            if attendance.time_out is not None:
                return Response({"detail": "Already recorded time out for today."}, status=status.HTTP_400_BAD_REQUEST)
            elif attendance.time_in is None:
                return Response({"detail": "Time in not recorded for today."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                now = timezone.now()
                attendance.time_out = now.time()
                attendance.save()
        except Attendance.DoesNotExist:
            return Response({"detail": "No time in record for today."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)
class AllAttendanceView(ListAPIView):
    queryset = Attendance.objects.all().order_by('-date')  # Get all attendance records, ordered by date
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated] 


class EmployeeAttendanceView(ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        
        return Attendance.objects.filter(employee_id=employee_id).order_by('-date')



class CreateProjectView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        response_data = ProjectSerializer(project).data
        return Response(response_data, status=status.HTTP_201_CREATED)

class GetAllProjectsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class UpdateProjectView(UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def update(self, request, *args, **kwargs):

        project = self.get_object()
        

        if project.manager != request.user:
            return Response({"message":"Only managers can update the status"},status=status.HTTP_403_FORBIDDEN)
        

        new_status = request.data.get('status')
        if new_status is None:
            return Response({"detail": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the project's status
        project.status = new_status
        project.save() 

        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
class UserProjectsView(ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(manager=user) | Project.objects.filter(employees=user)