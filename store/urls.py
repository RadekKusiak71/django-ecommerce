from django.urls import path
from .views import HomePage, ProductsPage

urlpatterns = [
    path('', HomePage.as_view(), name='store-home'),
    path('products/', ProductsPage.as_view(), name='products')
]
