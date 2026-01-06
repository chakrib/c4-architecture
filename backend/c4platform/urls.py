"""
URL configuration for C4 Platform project.
"""
from django.urls import path
from diagrams.api import api

urlpatterns = [
    path('api/', api.urls),
]
