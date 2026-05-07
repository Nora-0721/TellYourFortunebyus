# posts/urls.py
from django.urls import path

from mainsite import views
from .views import  test_set, test_get,xieyi,phone_xieyi,input_ch,phone_ch,download,home_phone_page

# from .views import CreatePostView 
urlpatterns = [
	path('phone_ch/', views.phone_ch, name='phone_input_ch'),
	path('home_phone/', views.home_phone_page, name='home_phone'),
	# path('phone_en/', PhonePostViewEn.as_view(), name='phone_input_en'),
	path('ch/', views.input_ch, name='input_ch'),
	# path('en/', CreatePostViewEn.as_view(), name='input_en'),
	path('', views.input_ch, name='add_post'),
	path('set/', views.test_set, name='set'),
	path('get/', views.test_get, name='get'),
	path('login/', views.loginMy, name='login'),
	path('xieyi/', views.xieyi, name='xieyi'),
	path('phone_xieyi/', views.phone_xieyi, name='xieyi'),
	path('download/', views.download, name='download'),
	path('pipei/', views.input_pipei, name='download1'),
	path('pipei_home/', views.home_phone_pipei, name='download2'),
	path('api/ideal_image_status/', views.ideal_image_status_api, name='ideal_image_status_api'),
]