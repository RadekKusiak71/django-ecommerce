from typing import Any
from decimal import Decimal
from django.db.models.query import QuerySet


from django.views import View
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView, FormMixin
from django.contrib import messages

from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem, Customer, Order, OrderItem
from .forms import UserRegisterForm, OrderForm


class ProfileUpdateView(UpdateView):
    template_name = 'profile.html'
    model = Customer
    fields = ['street', 'house_number', 'zip_code', 'city', 'country',]

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.errors:
            messages.error(
                self.request, 'Profile update failed. Please check the form for errors.')
        else:
            messages.success(self.request, 'Profile updated successfully.')
        return response

    def get_success_url(self):
        user_id = self.kwargs['pk']
        return reverse_lazy('profile-edit', kwargs={'pk': user_id})

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            user = self.request.user
            customer = Customer.objects.get(user=user)
            initial['street'] = customer.street
            initial['house_number'] = customer.house_number
            initial['zip_code'] = customer.zip_code
            initial['city'] = customer.city
            initial['country'] = customer.country

        return initial


class ProfileOrderView(LoginRequiredMixin, ListView):
    template_name = 'profile_orders.html'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Order.objects.filter(customer__user=self.request.user)
        return queryset


class CartItemDeleteView(DeleteView):
    model = CartItem
    success_url = reverse_lazy("cart")


class CartDetailView(FormMixin, ListView):
    template_name = 'cart.html'
    model = Cart
    form_class = OrderForm
    success_url = reverse_lazy('store-home')

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
        self.check_if_available(cart_items)

        return cart_items

    def check_if_available(self, cart_items: QuerySet[CartItem]) -> None:
        for item in cart_items:
            product = item.product
            if item.quantity > product.quantity:
                item.quantity = product.quantity
            item.save()
            if item.quantity == 0:
                item.delete()

    def form_valid(self, form: Any) -> HttpResponse:
        order = form.save(commit=False)
        if self.request.user.is_authenticated:
            customer = Customer.objects.get(user=self.request.user)
            cart = Cart.objects.get(customer=customer)
            order.customer = customer
        else:
            session_key = self.request.session.session_key
            order.session_id = session_key
            cart = Cart.objects.get(session_id=session_key)

        self.convert_cartitems_into_orderitems(
            cart=cart, order=order)

        return super().form_valid(form)

    def convert_cartitems_into_orderitems(self, cart: Cart, order: Order):
        items = CartItem.objects.filter(cart=cart)
        order.total = sum([item.total_price for item in items])
        order.save()
        for item in items:
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, subtotal=item.total_price)
            item.delete()
            item.product.quantity -= item.quantity
            item.product.save()
        cart.delete()

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            user = self.request.user
            customer = Customer.objects.get(user=user)
            initial['email'] = user.email
            initial['shipping_street'] = customer.street
            initial['shipping_house_number'] = customer.house_number
            initial['shipping_zip_code'] = customer.zip_code
            initial['shipping_city'] = customer.city
            initial['shipping_country'] = customer.country

        return initial

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ProductAddToCart(View):
    def post(self, request, product_id) -> HttpResponse:
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

    def get_cart(self) -> Cart:
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                customer=Customer.objects.get(user=self.request.user))
        else:
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_id=self.request.session.session_key)
        return cart

    def check_for_items(self, cart: Cart, product: Product, quantity: str) -> None:
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

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Checking if object is discounted
        if self.get_object().discount:
            context['discounted_price'] = round(self.get_object(
            ).price * Decimal(self.get_object().discount / 100), 2)

        context['more_like_this'] = self.get_more_like_this()
        return context

    def get_more_like_this(self) -> QuerySet[Product]:
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

    def get_filter_data(self) -> QuerySet[Product]:
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
