from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Product(models.Model): 
    name=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    shortdetail=models.CharField(max_length=200)
    description=models.CharField(max_length=2000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    image1=models.ImageField(upload_to='product_image')
    image2=models.ImageField(upload_to='product_image')
    image3=models.ImageField(upload_to='product_image')

    def __str__(self):
        return self.name

class Blog(models.Model):
    title=models.CharField(max_length=200)
    description1=models.CharField(max_length=2000)
    description2=models.CharField(max_length=2000)
    image=models.ImageField(upload_to='blog_image')
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    comment=models.CharField(max_length=1000)
    name=models.CharField(max_length=200)
    email=models.EmailField()
    website=models.CharField(max_length=500)
    blog_id=models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Contact(models.Model):
    address=models.CharField(max_length=200)
    number=models.IntegerField()
    email=models.EmailField()
    
    def __str__(self):
        return self.address
    
class Email(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField()
    text=models.CharField(max_length=500)
    
    def __str__(self):
        return self.name  
    
class Cartitem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart_key=models.CharField(max_length=200)
    name=models.CharField(max_length=200)
    price=models.IntegerField()
    image1 = models.URLField(max_length=500, null=True, blank=True)
    quantity=models.IntegerField()
    total=models.DecimalField(max_digits=100,decimal_places=2)
    size=models.CharField(max_length=200)
    color=models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    house_society_name = models.CharField(max_length=255)
    landmark_area = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    txnid = models.CharField(max_length=50, unique=True, blank=True, null=True)  # ✅ Add this field
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    number = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=20, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return self.name
    
class Rating(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    rating=models.IntegerField()
    name=models.CharField(max_length=200)
    detail=models.CharField(max_length=500)
    email=models.EmailField()
    
    def __str__(self):
        return self.name
    
    
    