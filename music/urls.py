from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'music'
urlpatterns = [
    path("create/", views.MusicCreateView.as_view(), name="music_create"),
    path("update/<int:pk>", views.MusicUpdateView.as_view(), name="music_update"),
    path("delete/<int:pk>", views.MusicDeleteView.as_view(), name="music_delete"),
    path("detail/<int:pk>", views.MusicDetailView.as_view(), name="music_detail"),
    path("list/", views.MusicListView.as_view(), name="music_list"),
    path("detail/<int:pk>/formation_create/", views.FormationCreateView.as_view(), name="formation_create"),
    path("detail/<int:pk>/formation_update/<uuid:formation_id>", views.FormationUpdateView.as_view(), name="formation_update"),
    path("detail/<int:pk>/formation_delete/<uuid:formation_id>", views.FormationDeleteView.as_view(), name="formation_delete"),
]
