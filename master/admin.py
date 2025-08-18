from django.contrib import admin
from .models import Product,Category,Blog,Comment,Contact,Email,Order,OrderItem,Rating,Cartitem

# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Email)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Rating)
admin.site.register(Cartitem)
