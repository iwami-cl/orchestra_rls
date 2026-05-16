from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'instrument'
urlpatterns = [
    path('parts/', views.InstrumentPartListView.as_view(), name='instrument_part_list'),
    path('parts/<uuid:pk>/detail/', views.InstrumentPartDetailView.as_view(), name='instrument_part_detail'),
    path('parts/create/', views.InstrumentPartCreateView.as_view(), name='instrument_part_create'),
    path('parts/<uuid:pk>/update/', views.InstrumentPartUpdateView.as_view(), name='instrument_part_update'),
    path('parts/<uuid:pk>/delete/', views.InstrumentPartDeleteView.as_view(), name='instrument_part_delete'),
]