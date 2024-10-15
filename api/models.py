from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import date
from django.utils import timezone
from cloudinary.models import CloudinaryField
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, role, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        
        user = self.model(email=email, first_name=first_name, last_name=last_name, role=role, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, role='admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, first_name, last_name, role, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    profile_picture=CloudinaryField("image",blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("employee", "Employee"),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='employee')
    salary = models.IntegerField()
    department = models.CharField(max_length=100)
    job_role = models.CharField(max_length=100)
    phone_number=models.CharField(max_length=30)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Report(models.Model):
    employee= models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    category=models.CharField(max_length=20)
    report=models.CharField(max_length=300)

    def __str__(self):
        return f"{self.employee} {self.report} {self.date} {self.category}"

class Leave(models.Model):
    LEAVE_STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    date_from = models.DateField()
    date_to = models.DateField()
    reason = models.CharField(max_length=300)
    status = models.CharField(max_length=20, default='pending', choices=LEAVE_STATUS)
    handled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_leaves')
    date_requested = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Leave request from {self.employee} from {self.date_from} to {self.date_to}"


class Attendance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Set default to the current date
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date} - In: {self.time_in} - Out: {self.time_out}"