from django.urls import path
import uuid
from . import views


app_name = 'schedule'

urlpatterns = [
    path('schedule/change/<uuid:pk>', views.ScheduleUpdateView.as_view(), name="schedule_update"),
    path('schedule/create/', views.ScheduleCreateView.as_view(), name="schedule_create"),
    path('schedule/detail/<uuid:pk>', views.ScheduleDetailView.as_view(), name="schedule_detail"),
    path('schedule/list/', views.ScheduleListView.as_view(), name="schedule_list"),
    path('schedule/delete/<uuid:pk>', views.ScheduleDeleteView.as_view(), name="schedule_delete"),
    path('attendance/check/<uuid:pk>', views.AttendanceCheckView.as_view(), name="attendance_check"),
    path('schedule_log/list/', views.ScheduleLogListView.as_view(), name="schedule_log_list"),
    path('schedule_log/detail/<uuid:pk>', views.ScheduleLogDetailView.as_view(), name="schedule_log_detail"),
    path('schedule_log/delete/<uuid:pk>', views.ScheduleLogDeleteView.as_view(), name="schedule_log_delete"),
]
