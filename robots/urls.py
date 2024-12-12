from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_robot, name='create_robot'),
    path('download_robots_summary/', views.generate_robot_summary, name='download_robots_summary')
]
