from django.urls import path
from .views import HomeListView

app_name = 'staff'

urlpatterns = [
    path('', HomeListView.as_view(), name='staff-home'),
]
