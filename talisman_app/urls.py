from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('entry/', views.transaction_entry_view, name='transaction_entry'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('income/', views.income_view, name='income'),
    path('expenses/', views.expenses_view, name='expenses'),
    path('reports/', views.reports_view, name='reports'),
    path('delete_transaction/<int:pk>/', views.delete_transaction_view, name='delete_transaction'),
]