from typing import Any
from django.shortcuts import render
from django.views.generic import ListView
from .models import Product


class HomePage(ListView):
    template_name = 'home.html'
    queryset = Product.objects.all().order_by('-sales_count')[0:10]
