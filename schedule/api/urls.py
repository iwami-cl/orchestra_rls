from django.urls import path
from . import views

app_name = "api-schedule"
urlpatterns = [
    path(r'schedule_list/', views.ScheduleListView.as_view(), name="api-schedule_list"),
    path(r'post_attendance/', views.AttendanceCreateUpdateAPIView.as_view(), name="api-attendance_update_short"),
    path(r'schedule/<uuid:pk>/attendance/', views.GetAttencanceForScheduleAPIView.as_view(), name="get_attendance_for_schedule"),
    path(r'schedule_log_list/', views.ScheduleLogListView.as_view(), name="api-schedule_log_list"),
]
