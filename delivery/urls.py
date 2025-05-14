from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path("admin/", admin.site.urls),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('cart/', views.add_to_cart, name='cart'),
    path('cart_list/', views.cart_view, name='cart_list'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_quantity/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('payment_page/', views.payment_page, name='payment_page'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('order_history/', views.order_history, name='order_history'),
    path('chatbot_response/', views.chatbot_response, name='chatbot_response'),
]