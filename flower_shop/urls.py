from django.urls import path
from .views import views
from .views import courier_views
from .views import admin_api
from .views import greenhouse_api
from .views import accountant_api
from flower_shop.views import manager_api


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

    path('api/species', greenhouse_api.list_species),
    path('api/plants/unready', greenhouse_api.list_unready_plants),
    path('api/plants/available_for_writeoff', greenhouse_api.list_available_for_writeoff),
    path('api/fertilizer/grouped', greenhouse_api.get_grouped_fertilizers),
    path('api/plants/plant-with-fertilizer', greenhouse_api.plant_with_fertilizer),
    path('api/plants/mark-ready', greenhouse_api.mark_ready),
    path('api/plants/writeoff', greenhouse_api.write_off),

    path('accountant', views.accountant, name='accountant_dashboard'),

    path('api/fertilizers', accountant_api.list_fertilizers),
    path('api/suppliers', accountant_api.list_suppliers),
    path('api/fertilizers/order', accountant_api.order_fertilizer_api),
    path('api/flowers/ready', accountant_api.list_ready_products),
    path('api/flowers/set-price', accountant_api.set_flower_price_api),

    path('manager', views.manager, name='manager_dashboard'),
    
    path('api/clients', manager_api.create_client),
    path('api/clients/list', manager_api.list_clients),
    path('api/flowers/list', manager_api.list_flowers),
    path('api/orders', manager_api.create_order_with_items_api),
    path('api/flowers/check-stock', manager_api.check_stock),
    path('api/orders/track', manager_api.track_order),
    path('api/orders/list', manager_api.list_orders_by_client),
]