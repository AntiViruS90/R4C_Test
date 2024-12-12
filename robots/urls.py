from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_robot, name='create_robot')
]
