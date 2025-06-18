from django.urls import path
from .views import views
from .views import courier_views
from .views import admin_api
from .views import greenhouse_views

urlpatterns = [
    path(r'', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('profile_details/', views.profile_details, name='profile_details'),
    path('client_orders/', views.client_orders, name='client_orders'),
    path('shop/', views.shop, name='shop'),
    path('shop/product_single/', views.product_single, name='product_single'),

    path('courier', views.courier, name='courier_dashboard'),

    path('api/courier/orders', courier_views.get_orders, name='get_orders'),
    path('api/courier/accept/<int:order_id>', courier_views.accept_order, name='accept_order'),
    path('api/courier/complete/<int:order_id>', courier_views.complete_order, name='complete_order'),

    path('admin', views.admin, name='admin_dashboard'),

    path('api/admin/add_genus/', admin_api.add_genus, name='add_genus'),
    path('api/admin/add_species_sql/', admin_api.add_species_sql, name='add_species_sql'),
    path('api/admin/add_fertilizer/', admin_api.add_fertilizer, name='add_fertilizer'),
    path('api/admin/link_genus_fertilizer_sql/', admin_api.link_genus_fertilizer_sql, name='link_genus_fertilizer_sql'),
    path('api/admin/add_supplier/', admin_api.add_supplier, name='add_supplier'),
    path('api/admin/add_courier_sql/', admin_api.add_courier_sql, name='add_courier_sql'),
    path('api/admin/get_genera/', admin_api.get_genera, name='get_genera'),
    path('api/admin/get_fertilizers/', admin_api.get_fertilizers, name='get_fertilizers'),

    path('gardener', views.greenhouse, name='greenhouse_dashboard'),

    # 🪴 Посадка
    path('api/species', greenhouse_views.list_species, name='get_species_list'),
    path('api/plants/plant-with-fertilizer', greenhouse_views.plant_with_fertilizer, name='plant_with_fertilizer'),
    path('api/fertilizer/grouped', greenhouse_views.get_grouped_fertilizers, name='get_grouped_fertilizers'),

    # ✅ Готовність до продажу
    path('api/plants/unready', greenhouse_views.list_unready_plants, name='get_unready_plants'),
    path('api/plants/mark-ready', greenhouse_views.mark_ready, name='mark_ready'),

    # 🗑️ Списання
    path('api/plants/all-for-writeoff', greenhouse_views.list_available_for_writeoff, name='get_all_plants_for_writeoff'),
    path('api/plants/write-off', greenhouse_views.write_off, name='write_off_flowers'),
]