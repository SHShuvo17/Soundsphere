from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/addresses/', views.addresses_view, name='addresses'),
    path('profile/addresses/<int:pk>/edit/', views.addresses_view, name='address_edit'),
    path('profile/addresses/<int:pk>/delete/', views.address_delete_view, name='address_delete'),
    path('profile/addresses/<int:pk>/set-default/', views.address_set_default_view, name='address_set_default'),
    path('profile/password-change/', views.password_change_view, name='password_change'),
    path('profile/change-password/', views.password_change_view, name='change_password'),
]
