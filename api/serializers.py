from rest_framework.serializers import ModelSerializer,SerializerMethodField
from .models import *
from rest_framework import serializers
from django.utils import timezone

class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields='__all__'

        extra_kwargs={'password':{"write_only":True}}
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)

class ReportSerializer(ModelSerializer):
    employee_name=SerializerMethodField()
    class Meta:
        model=Report
        fields=[
            'id',
            'employee_name',
            'date',
            'category',
            'report',
        ]
    def get_employee_name(self,obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"


class LeaveSerializer(ModelSerializer):
    employee_name = SerializerMethodField()
    handled_by_name = SerializerMethodField()
    date_requested=SerializerMethodField()

    class Meta:
        model = Leave
        fields = [
            "id",
            "date_requested",
            "employee_name",
            "date_from",
            "date_to",
            "status",
            "reason",
            "handled_by_name"
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_handled_by_name(self, obj):
        if obj.handled_by:
            return f"{obj.handled_by.first_name} {obj.handled_by.last_name}"
        return None
    def get_date_requested(self, obj):
        if obj.date_requested:
            return obj.date_requested.date()  # Convert datetime to date
        return None

class AttendanceSerializer(ModelSerializer):
    employee_name = SerializerMethodField()
    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "time_in",
            "time_out"
        ]
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
class ProjectSerializer(ModelSerializer):
    employees = serializers.ListField(
        child=serializers.EmailField(),  # Accepting a list of employee emails
        write_only=True,
        required=True
    )
    manager = serializers.EmailField(write_only=True)  # Accepting manager email

    manager_email = serializers.EmailField(source='manager.email', read_only=True)
    employee_emails = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = ['id','name', 'description', 'start_date', 'end_date', 'status', 'employees', 'manager', 'manager_email', 'employee_emails']

    def create(self, validated_data):
        employee_emails = validated_data.pop('employees')
        manager_email = validated_data.pop('manager')

        # Get employees based on email
        employees = User.objects.filter(email__in=employee_emails)
        
        # Get manager based on email
        try:
            manager = User.objects.get(email=manager_email)
            validated_data['manager'] = manager
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"manager": "Manager with this email does not exist."})

        project = Project.objects.create(**validated_data)
        project.employees.set(employees)  # Assign employees based on email
        return project

    def get_employee_emails(self, obj):
        return [employee.email for employee in obj.employees.all()]
