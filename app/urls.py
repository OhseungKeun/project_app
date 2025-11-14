"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login_view, name="login"),
    path('check-username/', views.check_username, name='check_username'),  
    path('logout/', views.logout_view, name='logout'), 
    path("quiz/", views.quiz_category_list, name="quiz_category_list"),
    path("quiz/<int:category_id>/", views.quiz_view, name="quiz_view"),
    path("quiz/<int:category_id>/submit/", views.quiz_submit, name="quiz_submit"),
    path("point/", views.point, name="point"),
    path("user/", views.user_info, name="user_info"),
]
