from django.urls import path
from . import views

app_name = 'dormitory'

urlpatterns = [
    path('my-room/', views.my_room, name='my_room'),
    path('buildings/', views.building_list, name='building_list'),
    path('section/<str:section>/', views.section_overview, name='section_overview'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('bed/<int:bed_id>/assign/', views.assign_bed, name='assign_bed'),
]
