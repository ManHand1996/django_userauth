from django.urls import path
from userctrl.api import application, manage
from rest_framework.routers import DefaultRouter

app_router = DefaultRouter()
app_router.register(r'applications', application.ApplicationViewSet, basename='app')
app_router.register(r'resources/[\w]+', manage.ResourceViewSet, basename='resource')
urlpatterns = [

]

urlpatterns += app_router.urls

