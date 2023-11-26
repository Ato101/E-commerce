from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import  render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import  force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count
    }

    return render(request, 'myshop/myshop.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    context = {
        'single_product': single_product
    }
    return render(request, 'myshop/product_detail.html', context)


def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()

    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    product_variation = []
    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variations = Variation.objects.filter(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)
                product_variation.extend(variations)
                print(product_variation)
            except Variation.DoesNotExist:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))

    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id_list = []

        for item in cart_item:
            existing_variation = item.variation.all()
            ex_var_list.append(list(existing_variation))
            id_list.append(item.id)

        if any(item == product_variation for item in ex_var_list):
            # Increase cart item quantity
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variation.clear()
                item.variation.add(*product_variation)

            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(product_variation) > 0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()

    return redirect('myshop:cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('myshop:cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(product=product, cart=cart)
    cart_item.delete()
    return redirect('myshop:cart')


@login_required(login_url='myshop:login')
def cart(request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
    try:
        cart = Cart.objects.get(cart_id=_cart_id((request)))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total

    }

    return render(request, 'myshop/cart.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count

    }

    return render(request, 'myshop/myshop.html', context)


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email= form.cleaned_data['email']
            username= form.cleaned_data['username']
            user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username)
            user.save()
            # user activation
            current_site = get_current_site(request)
            mail_subject ='please activate your account '
            message = render_to_string('myshop/account_verification.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Registration Successful')
            return redirect('myshop:signup')
    else:
        form = RegisterForm()

    return render(request, 'registration/signup.html', {'form': form})



def loginpage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect("home")
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'registration/login.html')

@login_required(login_url='myshop:login')
def logoutPage(request):
    logout(request)
    messages.success(request,'you are logout')
    return redirect('myshop:login')




def activate(request,uid64,token):
    try:
        uid =urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulation your accout is activated')
        return redirect('myshop:login')
    else:
        messages.error(request,'invalid activation link')
        return redirect(request,'myshop:signup')










