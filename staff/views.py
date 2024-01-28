from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import AccessMixin
from store.models import Order


class HomeListView(AccessMixin, ListView):
    template_name = 'staff-home.html'
    model = Order  # Use 'model' instead of 'queryset'
    context_object_name = 'orders'  # Specify a context object name
    login_url = 'store:store-home'  # Use the URL string directly

    def get_queryset(self):
        # You can customize the queryset if needed
        return Order.objects.all()
