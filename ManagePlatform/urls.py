"""ManagePlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dockermanage import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('overview/', views.Overview.as_view()),
    path('hosts/', views.Hosts.as_view()),
    path('ajax_host_mod/', views.ajax_host_mod),
    path('ajax_host_del/', views.ajax_host_del),
    path('containers/', views.Containers.as_view()),
    path('images/', views.Images.as_view()),
    path('containerAction/', views.containerAction.as_view()),
    path('callUpdateContainer/', views.callUpdateContainer)
]
