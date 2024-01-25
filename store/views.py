from typing import Any
from decimal import Decimal
from django.db.models.query import QuerySet


from django.views import View
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages

from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect

from .models import Product, Cart, CartItem, Customer
from .forms import UserRegisterForm


class CartDetailView(ListView):
    template_name = 'cart.html'
    model = Cart

    def get_queryset(self) -> QuerySet[Any]:
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                customer=Customer.objects.get(user=self.request.user))
        else:
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_id=self.request.session.session_key)
        cart_items = CartItem.objects.filter(cart=cart)
        print(cart_items)
        return cart_items


class ProductAddToCart(View):
    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)

        if not request.POST.get('quantity') or request.POST.get('quantity') == 0:
            quantity = 1
        else:
            quantity = request.POST.get('quantity')

        if product.quantity - int(quantity) >= 0:
            cart = self.get_cart()
            product.save()
            self.check_for_items(cart, product, quantity)
            return redirect('products')
        else:
            messages.error(request, f"There are only {
                           product.quantity} pieces available.")
            return redirect("product", product_id)

    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                customer=Customer.objects.get(user=self.request.user))
        else:
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_id=self.request.session.session_key)
        return cart

    def check_for_items(self, cart, product, quantity):
        if CartItem.objects.filter(cart=cart, product=product).exists():
            cart_item = CartItem.objects.filter(
                cart=cart, product=product).first()
            if cart_item.quantity >= product.quantity:
                messages.info(self.request, 'Can\'t add more')
            else:
                cart_item.quantity += int(quantity)
                cart_item.total_price = product.price * cart_item.quantity
                cart_item.save()
        else:
            total_price = product.price*int(quantity)
            CartItem.objects.create(
                cart=cart, product=product, quantity=quantity, total_price=total_price)


class UserLoginView(LoginView):
    template_name = 'login.html'
    next_page = reverse_lazy('store-home')


class UserCreateView(CreateView):
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('store-home')


class HomePage(ListView):
    template_name = 'home.html'
    queryset = Product.objects.all().order_by('-sales_count')[0:8]


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Checking if object is discounted
        if self.get_object().discount:
            context['discounted_price'] = round(self.get_object(
            ).price * Decimal(self.get_object().discount / 100), 2)

        context['more_like_this'] = self.get_more_like_this()
        return context

    def get_more_like_this(self):
        category = self.get_object().category
        products = Product.objects.filter(
            category=category, quantity__gt=0).exclude(title__contains=self.get_object().title).order_by('-sales_count')[0:3]
        return products


class ProductListView(ListView):
    template_name = 'products.html'
    queryset = Product.objects.all()
    paginate_by = 6

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['max_price'] = Product.objects.all().order_by(
            '-price').first().price
        return context

    def get_filter_data(self):
        if self.request.GET:
            title = self.request.GET.get('search')
            sort_type = self.request.GET.get('sort')
            available = self.request.GET.get('available')
            price_range = self.request.GET.get('price_range')
            category = self.request.GET.get('category')

            queryset = Product.objects.all()

            if title:
                queryset = queryset.filter(title__icontains=title)

            if sort_type == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_type == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort_type == 'popularity':
                queryset = queryset.order_by('-sales_count')

            if category:
                queryset = queryset.filter(category__id=category)

            if available:
                queryset = queryset.filter(price__gt=0)

            if price_range:
                queryset = queryset.filter(price__lte=price_range)

            if category:
                queryset = queryset.filter(category_id=category)
        else:
            queryset = Product.objects.all()

        return queryset

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        filtered_queryset = self.get_filter_data()
        self.queryset = filtered_queryset
        return super().get(request, *args, **kwargs)
