from rest_framework.serializers import ModelSerializer,SerializerMethodField
from .models import *

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