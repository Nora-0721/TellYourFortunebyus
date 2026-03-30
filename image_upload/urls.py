"""image_upload URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import re_path as url
from django.conf import settings # new
from django.urls import path, include # new
from django.views import static
from mainsite import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('home_phone/', views.home_phone_page,name = 'home_phone'),
	# path('home_phone_en/', views.home_phone_page_en,name = 'home_phone_en'),
	path('home_ch/', views.home_page_ch, name='home_ch'),
	path('home_en/', views.home_page_en, name='home_en'),
	path('', include('mainsite.urls')), # new
	url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static'),
	url(r'^media/(?P<path>.*)$', static.serve,{'document_root': settings.MEDIA_ROOT}, name='media'),
	# url("save/",views.saveDB,name="save"),
	# url("styleGanSave",views.styleGanSave,name="styleGanSave"),

]
