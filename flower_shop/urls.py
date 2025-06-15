from django.urls import path
from .views import views
from .views import courier_views

urlpatterns = [
    path(r'^$', views.home, name='home'),
    path('courier', courier_views.courier, name='courier_dashboard'),
    path('api/courier/orders', courier_views.get_orders, name='get_orders'),
    path('api/courier/accept/<int:order_id>', courier_views.accept_order, name='accept_order'),
    path('api/courier/complete/<int:order_id>', courier_views.complete_order, name='complete_order'),
]