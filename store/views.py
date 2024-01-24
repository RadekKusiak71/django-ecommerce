from typing import Any
from django.shortcuts import render
from django.views.generic import ListView
from .models import Product


class HomePage(ListView):
    template_name = 'home.html'
    queryset = Product.objects.all().order_by('-sales_count')[0:10]


class ProductsPage(ListView):
    template_name = 'products.html'
    queryset = Product.objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        max_price = Product.objects.all().order_by('-price').first()
        context['max_price'] = max_price.price
        return context
