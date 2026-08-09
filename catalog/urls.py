from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('suggest/', views.suggest, name='suggest'),
    path('customer-lookup/', views.customer_lookup, name='customer_lookup'),
    path('bulk-add/', views.bulk_add, name='bulk_add'),
]
