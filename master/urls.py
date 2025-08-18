from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index,name='index'),
    path('index/', views.index,name='index'),
    path('register', views.register,name='register'),
    path('login', views.user_login,name='user_login'),
    path('logout', views.user_logout,name='user_logout'),
    path('product-detail/<int:pk>', views.productdetail,name='product-detail'), 
    path('addtocart/<int:pk>', views.addtocart,name='addtocart'),
    path('remove_from_cart/<path:cart_key>',views.remove_from_cart,name='remove_from_cart'),
    path('searchlist', views.searchlist,name='searchlist'),
    path('categoryfilter/<int:pk>', views.categoryfilter,name='categoryfilter'),
    path('shopingcart', views.shopingcart,name='shopingcart'),
    path('blog/', views.blog,name='blog'),
    path('blog-detail/<int:pk>', views.blogdetail,name='blogdetail'),
    path('about', views.about,name='about'),
    path('contact', views.contact,name='contact'),
    path('update-cart/<str:cart_key>/<str:action>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('success/<int:order_id>/', views.success, name='success'),
    path("pay/", views.paymentrazor, name="payment"),
    # path("payment-success/", views.payment_success_razor, name="payment_success_razor"),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)