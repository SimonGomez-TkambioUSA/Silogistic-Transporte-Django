"""transporte URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib.admindocs import views
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.contrib.auth import views
from django.views.generic import TemplateView
from apps.catalogo.views import HomeViewTemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('', login_required(HomeViewTemplateView.as_view()), name='home'),
    path('catalogo/', include('apps.catalogo.urls', namespace='catalogo')),
    path('cliente/', include('apps.customer.urls', namespace='customer')),

]
