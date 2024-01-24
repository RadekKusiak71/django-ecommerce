from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from .models import Product
from django.core.paginator import Paginator


class HomePage(ListView):
    template_name = 'home.html'
    queryset = Product.objects.all().order_by('-sales_count')[0:8]


class ProductsPage(ListView):
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
