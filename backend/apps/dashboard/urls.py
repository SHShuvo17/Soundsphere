from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard_view, name='index'),
    path('orders/', views.admin_orders_view, name='orders'),
    path('orders/<str:order_number>/status/', views.admin_order_status_view, name='order_status'),
    path('orders/<str:order_number>/', views.admin_order_detail_view, name='order_detail'),
    path('customers/', views.admin_customers_view, name='customers'),
    path('customers/<int:pk>/toggle/', views.admin_customer_toggle_view, name='customer_toggle'),
    path('reviews/', views.admin_reviews_view, name='reviews'),
    path('reviews/<int:pk>/action/', views.admin_review_action_view, name='review_action'),
    path('reports/', views.admin_reports_view, name='reports'),
    path('reports/users.csv', views.admin_users_csv_view, name='users_csv'),
    path('<slug:resource>/', views.admin_resource_list_view, name='resource_list'),
    path('<slug:resource>/new/', views.admin_resource_form_view, name='resource_create'),
    path('<slug:resource>/<int:pk>/edit/', views.admin_resource_form_view, name='resource_edit'),
    path('<slug:resource>/<int:pk>/delete/', views.admin_resource_delete_view, name='resource_delete'),
]
