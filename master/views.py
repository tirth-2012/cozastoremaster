from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Category,Blog,Comment,Contact,Email,Order,OrderItem,Rating,Cartitem
from django.http import JsonResponse,HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib.auth.decorators import login_required
import uuid
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt


# RAZORPAY_KEY_ID = "rzp_test_1xCzvUttxPfa2F"
# RAZORPAY_KEY_SECRET = "61fKckOJxNoRx765d0UL8W6D"

# Create your views here.

def register(request):
    if request.method == "POST":
        username = request.POST["fullname"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        checkbox = 'checkbox' in request.POST

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect(register)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect(register)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect(user_login)

    return render(request, "registration.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(index)
        else:
            messages.error(request, "Invalid username or password!")
            return redirect(user_login)

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect(index)

def searchlist(request):
    query = request.GET.get('search', '')  # Get the search query from the request

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    else:
        products = Product.objects.all()  # Fetch all products if no query

    # Apply pagination to the search results
    paginator = Paginator(products, 1)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
        'query': query,
    })
    
def blog(request):
    blog=Blog.objects.all()
    paginator=Paginator(blog, 1)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        blog_list = []
        for blog in page_obj:
            blog_list.append({
                'id': blog.id,
                'title': blog.title,
                'description': blog.description1,
                'image_url': blog.image.url if blog.image else '',
            })
            
        return JsonResponse({
            'blog':blog_list,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous(),
            'next_page': page_obj.next_page_number()if page_obj.has_next() else None,
            'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })
        
    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })
        
    return render(request, 'blog.html', {
        'page_obj': page_obj,
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })
    
def index(request):
    products = Product.objects.all()
    paginator = Paginator(products, 12)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if AJAX request
        product_list = []
        for product in page_obj:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image_url': product.image1.url if product.image1 else '/static/default_image.jpg'
            })

        return JsonResponse({
            'products': product_list,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous(),
            'next_page': page_obj.next_page_number()if page_obj.has_next() else None,
            'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })

    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })

def categoryfilter(request,pk):
    p=get_object_or_404(Category,pk=pk)
    post=Product.objects.filter(category=p)
    paginator = Paginator(post, 1)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if AJAX request
        product_list = []
        for product in page_obj:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image_url': product.image1.url if product.image1 else '/static/default_image.jpg'
            })

        return JsonResponse({
            'products': product_list,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous(),
            'next_page': page_obj.next_page_number()if page_obj.has_next() else None,
            'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })
    
    cat=Category.objects.all()
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'categoryfilter.html', {
        'page_obj':page_obj,
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })

def addtocart(request, pk):
    """Add product to the session-based cart with size & color handling"""
    cart = request.session.get('cart', {})  # Get cart from session
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size', '').strip()
    color = request.POST.get('color', '').strip()

    # 🔹 Create a unique cart key: product ID + size + color
    cart_key = f"{pk}_{size}_{color}"

    if cart_key in cart:
        # 🔹 If product with same size & color exists, update quantity
        cart[cart_key]['quantity'] += quantity
        messages.success(request, "Product quantity updated in cart!")
    else:
        # 🔹 Otherwise, add as a new cart item
        product = get_object_or_404(Product, id=pk)
        cart[cart_key] = {
            'name': product.name,
            'price': float(product.price),  # Ensure price is stored as float
            'image': product.image1.url if product.image1 else '/static/default_image.jpg',
            'quantity': quantity,
            'size': size,
            'color': color,
        }
        messages.success(request, "Product added to cart successfully!")

    request.session['cart'] = cart  # Save cart back to session

    referer_url = request.META.get('HTTP_REFERER', '')  # Stay on the same page
    return redirect(referer_url if referer_url else "index")

def remove_from_cart(request, cart_key):
    """Remove product from cart or decrease quantity"""
    
    cart = request.session.get('cart', {})

    if cart_key in cart:
        if cart[cart_key]['quantity'] > 1:
            cart[cart_key]['quantity'] -= 1  # 🔹 Decrease quantity by 1
            messages.success(request, "Product quantity decreased in cart!")
        else:
            del cart[cart_key]  # 🔹 Remove item if quantity reaches 0
            messages.success(request, "Product removed from cart!")

    request.session['cart'] = cart  # Update session cart
    return redirect('index')

def shopingcart(request):
    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'shoping-cart.html', {
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })
    

def productdetail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size': item.get('size', ''),
            'color': item.get('color', ''),
        })
        
    ratings = Rating.objects.filter(product=product)

    if request.method == "POST":
        rating = request.POST.get("rating")
        name = request.POST.get("name")
        email = request.POST.get("email")
        detail = request.POST.get("detail")

        if rating and rating.isdigit():
            rating = int(rating)
            if 1 <= rating <= 5:
                Rating.objects.create(product=product, rating=rating, detail=detail, name=name, email=email)
                return redirect(productdetail, pk=product.id)

    return render(request, 'product-detail.html', {
        'product': product,
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
        "ratings": ratings,
    })

def about(request):
    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'about.html', {
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        text = request.POST.get('msg')

        if name  and text and email:  # Ensure required fields are provided
            email = Email.objects.create(
                name=name,
                email=email,    
                text=text,
            )
            email.save()
    contact=Contact.objects.all()
    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'contact.html', {
        'contact':contact,
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })
    
def blogdetail(request,pk):
    blogs=get_object_or_404(Blog,pk=pk)
    comments=Comment.objects.filter(blog_id=pk)
    if request.method == 'POST':
        comment_text  = request.POST.get('comment')
        name = request.POST.get('name')
        email = request.POST.get('email')
        website = request.POST.get('website')
        blog_id=request.POST.get('blog')

        if comment_text  and name and email:  # Ensure required fields are provided
            comment = Comment.objects.create(
                comment=comment_text,
                name=name,
                email=email,
                website=website,
                blog_id=blog_id,
            )
            comment.save()
    
    cat = Category.objects.only("id", "name")
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for cart_key, item in cart.items():
        try:
            price = int(float(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = 0
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size':item['size'],
            'color':item['color'],
        })

    return render(request, 'blogdetail.html', {
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart),
        'total_price': total_price,
    })

def update_cart(request, cart_key, action):
    cart = request.session.get('cart', {})

    if str(cart_key) in cart:
        if action == "increase":
            cart[str(cart_key)]['quantity'] += 1  # Increase quantity
            messages.success(request, "Product quantity increased successfully!")
        elif action == "decrease":
            if cart[str(cart_key)]['quantity'] > 1:
                cart[str(cart_key)]['quantity'] -= 1  # Decrease quantity
                messages.success(request, "Product quantity decreased successfully!")
            else:
                del cart[str(cart_key)]
                messages.success(request, "Product removed from cart!")
    else:
            cart[cart_key] = {'quantity': 1}
            messages.success(request, "Product added to cart successfully!")

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('shopingcart')
        

@login_required(login_url='user_login')
def checkout(request):
    # Retrieve cart from session
    session_cart = request.session.get('cart', {})

    # Prepare cart items and calculate total price
    cart_items = []
    total_price = Decimal('0.00')

    for cart_key, item in session_cart.items():
        try:
            price = Decimal(str(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = Decimal('0.00')
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size': item.get('size', ''),
            'color': item.get('color', ''),
        })

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        house_society_name = request.POST.get("house_society_name")
        landmark_area = request.POST.get("landmark_area")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin_code = request.POST.get("pin_code")

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect("checkout")

        # ✅ Create Razorpay Order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(total_price * 100),  # in paisa
            'currency': 'INR',
            'payment_capture': 1
        })

        # ✅ Save Order in database with Razorpay Order ID
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            house_society_name=house_society_name,
            landmark_area=landmark_area,
            city=city,
            state=state,
            pin_code=pin_code,
            total_price=total_price,
            razorpay_order_id=razorpay_order['id']
        )

        # ✅ Redirect to payment page with all necessary info
        return render(request, 'payment.html', {
            'order': order,
            'order_id': order.id,  # Pass Django order ID
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': int(total_price * 100),
        })

    # Fetch categories
    cat = Category.objects.only("id", "name")

    return render(request, 'checkout.html', {
        'cat': cat,
        'cart_items': cart_items,
        'cart_count': len(cart_items),
        'total_price': total_price,
    })


@csrf_exempt
def paymentrazor(request):
    session_cart = request.session.get('cart', {})
    
    # Prepare cart items and calculate total price
    cart_items = []
    total_price = Decimal('0.00')
    
    for cart_key, item in session_cart.items():
        try:
            price = Decimal(str(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except (ValueError, TypeError):
            price = Decimal('0.00')
            quantity = 0

        item_total = price * quantity
        total_price += item_total

        cart_items.append({
            'cart_key': cart_key,
            'name': item.get('name', 'Unknown Product'),
            'price': price,
            'image1': item.get('image', 'default_image.jpg'),
            'quantity': quantity,
            'total': item_total,
            'size': item.get('size', ''),
            'color': item.get('color', ''),
        })
        
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    price=int(total_price*100) 
    
    # Order details
    data = {
        "amount": price,  # Amount in paise (₹500)
        "currency": "INR",
        "payment_capture": 1  # Auto capture
    }
    order = client.order.create(data)

    return render(request, "payment.html", {"order_id": order["id"], "razorpay_key": settings.RAZORPAY_KEY_ID})

@csrf_exempt
def payment_success(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    print(order.id)
    orders = order.id

    cart = request.session.get('cart', {})
    
    for item in cart.values():
        try:
            price = Decimal(str(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
        except:
            continue

        OrderItem.objects.create(
            order=order,
            number=orders,
            name=item.get('name', ''),
            size=item.get('size', ''),
            color=item.get('color', ''),
            quantity=quantity,
            price=price
        )

    # Optional: Save Razorpay payment ID if needed
    # payment_id = request.POST.get('razorpay_payment_id')
    # if payment_id:
    #     order.payment_id = payment_id 
    #     order.save()

    request.session['cart'] = {}
    return redirect('success', order_id=order.id)


def success(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'success.html', {'order': order, 'items': items})

