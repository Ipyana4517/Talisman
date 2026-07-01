from django.contrib import admin
from .models import FinancialCategory, Transaction, DailyMotivation

admin.site.register(FinancialCategory)
admin.site.register(Transaction)
admin.site.register(DailyMotivation)