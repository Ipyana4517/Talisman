from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FinancialCategory(models.Model):
    CATEGORY_TYPES = [
        ('ASSET', 'Asset (Cash, Accounts Receivable)'),
        ('LIABILITY', 'Liability (Accounts Payable, Loans)'),
        ('EQUITY', 'Equity (Capital, Retained Earnings)'),
        ('INCOME', 'Income / Inflow'),
        ('EXPENSE', 'Expense / Outflow'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_categories')

    class Meta:
        verbose_name_plural = "Financial Categories"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name='transactions')
    date = models.DateField(default=timezone.now)
    is_reconciled = models.BooleanField(default=True, help_text="False if it's a pending Payable/Receivable")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True, help_text="Optional remarks for the transaction.")

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} | {self.title} | {self.amount}"


class DailyMotivation(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=100, default="Unknown")

    def __str__(self):
        return f'"{self.quote}" - {self.author}'