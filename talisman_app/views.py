from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from .models import FinancialCategory, Transaction
from decimal import Decimal
import datetime
from django.shortcuts import get_object_or_404

# ==============================================================================
# 1. CENTRAL CONTROL DASHBOARD
# ==============================================================================
def dashboard_view(request):
    transactions = Transaction.objects.all()
    
    def get_sum(cat_type):
        res = transactions.filter(category__type=cat_type).aggregate(total=Sum('amount'))['total']
        return res if res else Decimal('0.00')

    inflows = get_sum('INCOME')
    outflows = get_sum('EXPENSE')
    assets = get_sum('ASSET')
    liabilities = get_sum('LIABILITY')
    equity = get_sum('EQUITY')

    net_operating_profit = inflows - outflows
    cashflow_efficiency = (net_operating_profit / inflows * 100) if inflows > 0 else 0
    
    # Debt to Equity calculation for dashboard metrics
    if equity > 0:
        debt_to_equity_ratio = round((liabilities / equity) * 100, 1)
    else:
        debt_to_equity_ratio = 0.0

    pending_deadlines = transactions.filter(is_reconciled=False)[:5]

    motivation = {
        "quote": "Track your wealth diligently; a talisman only protects what you value.",
        "author": "System Engine"
    }

    # Dashboard notifications configuration
    notifications = [
        {
            "type": "SUCCESS",
            "message": "Talisman Core ledger balance engine initialized cleanly.",
            "timestamp": timezone.now()
        }
    ]

    context = {
        'current_profile': 'Edwin',
        'inflows': inflows,
        'outflows': outflows,
        'assets': assets,
        'liabilities': liabilities,
        'total_income': inflows,
        'total_expenses': outflows,
        'debt_to_equity_ratio': debt_to_equity_ratio,
        'pending_payments_total': liabilities, # Fallback mapping or pending calculations
        'cashflow_efficiency': round(cashflow_efficiency, 1),
        'pending_deadlines': pending_deadlines,
        'motivation': motivation,
        'notifications': notifications,
        'current_time': timezone.now(),
    }
    return render(request, 'talisman_app/dashboard.html', context)


# ==============================================================================
# 2. TRANSACTION POSTING ENGINE
# ==============================================================================
def transaction_entry_view(request):
    default_user = User.objects.first()

    if request.method == "POST":
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        is_reconciled = request.POST.get('is_reconciled') == 'true'
        
        category = FinancialCategory.objects.get(id=category_id)
        
        Transaction.objects.create(
            user=default_user,
            category=category,
            title=title,
            amount=Decimal(amount),
            date=timezone.now().date(),
            is_reconciled=is_reconciled
        )
        return redirect('dashboard')

    categories = FinancialCategory.objects.all().order_by('type', 'name')
    return render(request, 'talisman_app/transaction_entry.html', {'categories': categories})


# ==============================================================================
# 3. CHART OF ACCOUNTS & COA MANAGER
# ==============================================================================
# ==============================================================================
# 3. CHART OF ACCOUNTS & COA MANAGER (Aggregated Summary Setup)
# ==============================================================================
def accounts_view(request):
    default_user = User.objects.first()

    if request.method == "POST":
        name = request.POST.get('name')
        category_type = request.POST.get('type')
        
        FinancialCategory.objects.create(
            user=default_user,
            name=name,
            type=category_type
        )
        return redirect('accounts')

    # Establish the 5 foundational columns
    core_pillars = {
        'ASSET': {'name': 'Asset Registers', 'categories': {}, 'total': Decimal('0.00')},
        'LIABILITY': {'name': 'Liabilities & Obligations', 'categories': {}, 'total': Decimal('0.00')},
        'EQUITY': {'name': 'Equity & Capital Accounts', 'categories': {}, 'total': Decimal('0.00')},
        'INCOME': {'name': 'Operational Income / Revenue', 'categories': {}, 'total': Decimal('0.00')},
        'EXPENSE': {'name': 'Operating Expense Accounts', 'categories': {}, 'total': Decimal('0.00')},
    }

    # Group every category into its strict foundational type bucket
    all_categories = FinancialCategory.objects.all()
    for cat in all_categories:
        c_type = cat.type.upper()
        if c_type in core_pillars:
            core_pillars[c_type]['categories'][cat.id] = {
                'id': cat.id,
                'name': cat.name,
                'total': Decimal('0.00')
            }

    # Populate and aggregate totals based on recorded transactions
    all_transactions = Transaction.objects.all()
    for tx in all_transactions:
        tx_type = tx.category.type.upper()
        cat_id = tx.category.id
        if tx_type in core_pillars and cat_id in core_pillars[tx_type]['categories']:
            core_pillars[tx_type]['categories'][cat_id]['total'] += tx.amount
            core_pillars[tx_type]['total'] += tx.amount

    # Convert dictionary structure into flat iterable lists for template looping
    ledger_data = []
    for p_key, p_data in core_pillars.items():
        ledger_data.append({
            'pillar_key': p_key,
            'pillar_name': p_data['name'],
            'sub_categories': p_data['categories'].values(),
            'total': p_data['total']
        })

    context = {
        'current_profile': 'Edwin',
        'ledger_data': ledger_data,
        'category_choices': [
            ('ASSET', 'Asset / Cash Account'),
            ('LIABILITY', 'Liabilities Account'),
            ('EQUITY', 'Owner Equity / Capital'),
            ('INCOME', 'Income / Revenue Streams'),
            ('EXPENSE', 'Operational Expense')
        ]
    }
    return render(request, 'talisman_app/accounts.html', context)

# ==============================================================================
# 4. SUBSIDIARY JOURNALS (INFLOW & OUTFLOW LEDGERS)
# ==============================================================================
def income_view(request):
    records = Transaction.objects.filter(category__type='INCOME').order_by('-date')
    total_income = records.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    return render(request, 'talisman_app/income.html', {'records': records, 'total_income': total_income})

def expenses_view(request):
    records = Transaction.objects.filter(category__type='EXPENSE').order_by('-date')
    total_expenses = records.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    return render(request, 'talisman_app/expenses.html', {'records': records, 'total_expenses': total_expenses})


# ==============================================================================
# 5. STRATEGIC REVENUE & AUDIT INTELLIGENCE (DRILL-DOWN REVENUE/EXPENSE)
# ==============================================================================
def reports_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    today = timezone.now().date()
    start_date = datetime.date(today.year, 1, 1) if not start_date_str else datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.date(today.year, 12, 31) if not end_date_str else datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

    all_transactions = Transaction.objects.all()

    # Calculate Opening Balance (Prior balance historical pipeline before window start)
    prior_inflows = all_transactions.filter(category__type='INCOME', date__lt=start_date).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    prior_outflows = all_transactions.filter(category__type='EXPENSE', date__lt=start_date).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    opening_balance = prior_inflows - prior_outflows

    period_transactions = all_transactions.filter(date__range=[start_date, end_date])

    def get_period_sum(cat_type):
        res = period_transactions.filter(category__type=cat_type).aggregate(total=Sum('amount'))['total']
        return res if res else Decimal('0.00')

    inflows = get_period_sum('INCOME')
    outflows = get_period_sum('EXPENSE')
    assets = get_period_sum('ASSET')
    liabilities = get_period_sum('LIABILITY')
    equity = get_period_sum('EQUITY')

    closing_balance = opening_balance + inflows - outflows

    # Helper to construct breakdown matrices for a given type string
    def build_category_breakdown(cat_type_string):
        breakdown_list = []
        for cat in FinancialCategory.objects.filter(type=cat_type_string):
            cat_transactions = period_transactions.filter(category=cat).order_by('-date')
            amt = cat_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            last_tx = cat_transactions.first()
            last_date_recorded = last_tx.date.strftime('%Y-%m-%d') if last_tx else "No records"
            
            breakdown_list.append({
                'id': cat.id,
                'name': cat.name,
                'amount': amt,
                'last_date': last_date_recorded,
                'lines': cat_transactions
            })
        return breakdown_list

    # Construct the breakdowns for all five functional accounting classifications
    equity_breakdown = build_category_breakdown('EQUITY')
    asset_breakdown = build_category_breakdown('ASSET')
    liability_breakdown = build_category_breakdown('LIABILITY')
    expense_breakdown = build_category_breakdown('EXPENSE')
    income_breakdown = build_category_breakdown('INCOME')

    # Dynamic Month Key Allocation Builder 
    monthly_data = {}
    current_loop_date = start_date
    while current_loop_date <= end_date:
        month_key = current_loop_date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'label': current_loop_date.strftime('%B %Y'),
                'income': Decimal('0.00'),
                'expense': Decimal('0.00'),
                'net_margin': Decimal('0.00')
            }
        current_loop_date += datetime.timedelta(days=28)

    for tx in period_transactions:
        m_key = tx.date.strftime('%Y-%m')
        if m_key in monthly_data:
            if tx.category.type == 'INCOME':
                monthly_data[m_key]['income'] += tx.amount
            elif tx.category.type == 'EXPENSE':
                monthly_data[m_key]['expense'] += tx.amount

    for m_key in monthly_data:
        monthly_data[m_key]['net_margin'] = monthly_data[m_key]['income'] - monthly_data[m_key]['expense']

    net_operating_profit = inflows - outflows
    efficiency_rate = (net_operating_profit / inflows * 100) if inflows > 0 else 0
    debt_to_equity = (liabilities / equity * 100) if equity > 0 else 0

    context = {
        'current_profile': 'Edwin',
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'inflows': inflows,
        'outflows': outflows,
        'opening_balance': opening_balance,
        'closing_balance': closing_balance,
        'net_operating_profit': net_operating_profit,
        'efficiency_rate': round(efficiency_rate, 1),
        'debt_to_equity': round(debt_to_equity, 1),
        'equity_breakdown': equity_breakdown,
        'asset_breakdown': asset_breakdown,
        'liability_breakdown': liability_breakdown,
        'expense_breakdown': expense_breakdown,
        'income_breakdown': income_breakdown,
        'monthly_trends': sorted(monthly_data.values(), key=lambda x: datetime.datetime.strptime(x['label'], '%B %Y')),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'current_time': timezone.now(),
    }
    return render(request, 'talisman_app/reports.html', context)


# ==============================================================================
# 6. TRANSACTION DELETION HANDLER
# ==============================================================================
def delete_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.delete()
    return redirect(request.META.get('HTTP_REFERER', 'accounts'))