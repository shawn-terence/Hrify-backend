"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from api.views import*
urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/create/",CreateUserView.as_view(),name="register-users"),
    path("user/login/",Login.as_view(),name="login-users"),
    path("user/logout/",Logout.as_view(),name="logout-users"),
    path('user/<int:pk>/details/', UserDetailsView.as_view(), name='user-details'),
    path('user/update/',UpdateProfile.as_view(),name='update'),
    path('user/password/',UpdatePasswordView.as_view(),name='password-update'),
    path('report/<int:user_id>/',MakeReportView.as_view(),name="make-report"),
    path('report/',EmployeeReportView.as_view(),name="report"),
    path('report/adm/',AdminReportView.as_view(),name='reportlist'),
    path('report/categories/', ReportCategoryListView.as_view(), name="report-categories"),
    path('report/update/<int:id>/',UpdateReportView.as_view(),name='update-report'),
    path('report/delete/<int:id>/',DeleteReportView.as_view(),name='delete-report'),
    path('leave/request/',RequestLeaveView.as_view(),name='leave-request'),
    path('leave/action/<int:id>/',RequestActionView.as_view(),name='leave-action'),
    path('leave/delete/<int:pk>/', DeleteLeaveRequestView.as_view(), name='delete-leave-request'),
    path('leaves/', LeaveListView.as_view(), name='leave-list'),
    path('attendance/', AllAttendanceView.as_view(), name='all-attendance'),
    path('attendance/<int:employee_id>/', EmployeeAttendanceView.as_view(), name='employee-attendance'),
    path('time-in/', TimeInView.as_view(), name='time_in'),
    path('time-out/', TimeOutView.as_view(), name='time_out'),
]
