from django.core.management.base import BaseCommand
from datetime import date, timedelta
from django.utils.timezone import now
from api.models import *

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting seeding process...")

        # Clear existing data
        self.stdout.write("Deleting old data...")
        User.objects.all().delete()
        Leave.objects.all().delete()
        Report.objects.all().delete()
        Attendance.objects.all().delete()
        Project.objects.all().delete()

        self.stdout.write("Old data deleted.")

        # Create admins
        jane = User.objects.create_user(
            email="jane.doe@example.com",
            first_name="Jane",
            last_name="Doe",
            role="admin",
            salary=120000,
            department="HR",
            job_role="HR Manager",
            phone_number="123-456-7890",
            password="password123",
        )

        admin2 = User.objects.create_user(
            email="admin2@example.com",
            first_name="Admin",
            last_name="Two",
            role="admin",
            salary=110000,
            department="IT",
            job_role="System Administrator",
            phone_number="234-567-8901",
            password="password123",
        )

        # Create employees
        john = User.objects.create_user(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            role="employee",
            salary=80000,
            department="Finance",
            job_role="Accountant",
            phone_number="345-678-9012",
            password="password123",
        )

        employees = [john]

        for i in range(1, 21): 
            employees.append(
                User.objects.create_user(
                    email=f"employee{i}@example.com",
                    first_name=f"Employee",
                    last_name=f"{i}",
                    role="employee",
                    salary=70000 + i * 1000,
                    department="Sales",
                    job_role="Sales Executive",
                    phone_number=f"456-789-901{i}",
                    password="password123",
                )
            )

        # Create leave requests for employees
        self.stdout.write("Creating leave requests...")
        for employee in employees:
            Leave.objects.create(
                employee=employee,
                date_from=date.today() - timedelta(days=5),
                date_to=date.today() - timedelta(days=2),
                reason="Family emergency",
                status="approved",
                handled_by=jane,
            )
            Leave.objects.create(
                employee=employee,
                date_from=date.today() + timedelta(days=5),
                date_to=date.today() + timedelta(days=10),
                reason="Vacation",
                status="pending",
            )

        # Create reports for employees
        self.stdout.write("Creating reports...")
        for employee in employees:
            Report.objects.create(
                employee=employee,
                date=now().date(),
                category="Weekly Update",
                report=f"Report submitted by {employee.first_name} for the week.",
            )

        # Create attendance records for employees
        self.stdout.write("Creating attendance records...")
        for employee in employees:
            Attendance.objects.create(
                employee=employee,
                date=now().date() - timedelta(days=1),
                time_in=now().time(),
                time_out=(now() + timedelta(hours=8)).time(),
            )

        # Create projects
        self.stdout.write("Creating projects...")
        project1 = Project.objects.create(
            name="Project Alpha",
            description="A high-priority project.",
            start_date=now().date() - timedelta(days=30),
            end_date=now().date() + timedelta(days=90),
            status="in_progress",
            manager=jane,
        )
        project1.employees.add(*employees)

        project2 = Project.objects.create(
            name="Project Beta",
            description="A secondary project.",
            start_date=now().date() - timedelta(days=10),
            status="not_started",
            manager=admin2,
        )
        project2.employees.add(john)

        self.stdout.write("Seeding completed successfully!")
