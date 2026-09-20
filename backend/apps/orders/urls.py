from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='confirmation'),
    path('history/', views.order_history_view, name='history'),
    path('detail/<str:order_number>/', views.order_detail_view, name='detail'),
    path('cancel/<str:order_number>/', views.cancel_order_view, name='cancel'),
]
