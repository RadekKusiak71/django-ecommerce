from django.urls import path
from .views import HomePage, ProductListView, ProductDetailView, ProfileOrderView, ProfileUpdateView, CartItemDeleteView, CartDetailView, UserCreateView, UserLoginView, ProductAddToCart
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


app_name = 'store'

urlpatterns = [
    path('', HomePage.as_view(), name='store-home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('store-home')), name='logout'),
    path('product/<int:product_id>/add/',
         ProductAddToCart.as_view(), name='add-product'),
    path('product/<int:pk>/delete/',
         CartItemDeleteView.as_view(), name='delete-product'),
    path('cart/',
         CartDetailView.as_view(), name='cart'),
    path('profile/',
         ProfileOrderView.as_view(), name='profile'),
    path('profile/<int:pk>/',
         ProfileUpdateView.as_view(), name='profile-edit'),
]
