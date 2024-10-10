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