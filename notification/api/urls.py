from django.urls import path
from . import views

app_name = "api-notification"
urlpatterns = [
    path(r'get_notifications/', views.GetNotificationsView.as_view(), name="api-get_notifications"),
]