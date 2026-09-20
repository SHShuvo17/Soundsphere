from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_view, name='wishlist'),
    path('index/', views.wishlist_view, name='index'),
]
