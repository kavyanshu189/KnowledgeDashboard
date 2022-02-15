from xml.etree.ElementInclude import include
from django import views
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from authentication import views

urlpatterns = [
   path('', views.index, name="home"),
   path('signup', views.signup, name="signup"),
   path("about", views.about, name='about'),
   path("contact", views.contact, name='contact'),
   path('signin', views.signin, name="signin"),
   path('signout', views.signout, name="signout"),
   path('activate/<uidb64>/<token>/', views.activate, name="activate")
   
]