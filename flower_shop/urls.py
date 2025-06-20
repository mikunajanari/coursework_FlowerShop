from django.urls import path
from .views import views
from .views import courier_api
from .views import admin_api
from .views import greenhouse_api
from .views import accountant_api
from .views import manager_api
from .views import login_api
from .views import shop_api
from .views import signup_api


urlpatterns = [
    path(r'', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('login/', login_api.login_pg, name='login'),
    path('signup/', signup_api.signup, name='signup'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('profile_details/', views.profile_details, name='profile_details'),
    path('client_orders/', views.client_orders, name='client_orders'),
    path('shop/', shop_api.shop, name='shop'),
    path('shop/product_single/<int:product_id>/', shop_api.product_single, name='product_single'),
    path('logout/', views.logout_view, name='logout'),

    path('courier', views.courier, name='courier_dashboard'),

    path('api/courier/orders-for-delivery', courier_api.orders_for_delivery),
    path('api/courier/assign-order', courier_api.assign_courier),
    path('api/courier/taken-orders', courier_api.orders_taken_by_courier),
    path('api/courier/update-status', courier_api.update_order_status),

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
    path('api/accountant/expenses-report', accountant_api.expenses_report),
    path('api/accountant/income-report', accountant_api.income_report),

    path('manager', views.manager, name='manager_dashboard'),
    
    path('api/clients', manager_api.create_client),
    path('api/clients/list', manager_api.list_clients),
    path('api/flowers/list', manager_api.list_flowers),
    path('api/orders', manager_api.create_order_with_items_api),
    path('api/flowers/check-stock', manager_api.check_stock),
    path('api/orders/track', manager_api.track_order),
    path('api/orders/list', manager_api.list_orders_by_client),
    path('api/orders/monthly-trends', manager_api.monthly_order_trends),
    path('api/genus/ranking', manager_api.genus_ranking),
    path('api/flowers/demand', manager_api.flower_demand),
    path('api/seasons/stats', manager_api.season_stats),
    path('api/clients/preferences', manager_api.client_preferences),
    path('api/couriers/performance', manager_api.courier_performance),
    path('api/species/most-popular', manager_api.most_popular_species),
]