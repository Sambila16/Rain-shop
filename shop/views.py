from datetime import timedelta
from decimal import Decimal
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import (CategoryForm, CustomerForm, LoanPaymentForm, ProductForm,
                    SaleForm, ShopkeeperForm, UnitForm)
from .models import Category, Customer, LoanPayment, Product, Sale, Unit

def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('sell')
        return view(request, *args, **kwargs)
    return wrapped

def index(r):
    return render(r, 'index.html')

@staff_required
def admin_dashboard(r):
    today = timezone.localdate()
    todays = Sale.objects.filter(date__date=today)
    keeper_form = ShopkeeperForm(r.POST or None, prefix='keeper')
    if r.method == 'POST' and r.POST.get('action') == 'create_shopkeeper':
        if keeper_form.is_valid():
            keeper_form.save()
            messages.success(r, f'Shopkeeper “{keeper_form.cleaned_data["name"]}” created.')
            return redirect('admin_dashboard')
    return render(r, 'admin_dashboard.html', {
        'product_count': Product.objects.count(),
        'customer_count': Customer.objects.count(),
        'sales_count': Sale.objects.count(),
        'today_total': sum(s.total for s in todays),
        'low': [p for p in Product.objects.all() if p.low],
        'recent': Sale.objects.select_related('product', 'customer')[:8],
        'keeper_form': keeper_form,
    })

@staff_required
def shop_setup(r):
    category_form = CategoryForm(r.POST or None, prefix='category')
    unit_form = UnitForm(r.POST or None, prefix='unit')
    if r.method == 'POST':
        action = r.POST.get('action')
        form = category_form if action == 'add_category' else unit_form if action == 'add_unit' else None
        if form and form.is_valid():
            item = form.save()
            messages.success(r, f'{item} added.')
            return redirect('shop_setup')
    return render(r, 'shop_setup.html', {
        'category_form': category_form, 'unit_form': unit_form,
        'categories': Category.objects.all(), 'units': Unit.objects.all(),
    })

@staff_required
def dashboard(r):
    today = timezone.localdate()
    todays = Sale.objects.filter(date__date=today)
    return render(r, 'dashboard.html', {
        'total': sum(s.total for s in todays), 'count': todays.count(),
        'low': [p for p in Product.objects.all() if p.low],
        'expiring': Product.objects.filter(expiry__isnull=False, expiry__lte=today + timedelta(days=30)),
        'recent': Sale.objects.select_related('product')[:8]})

@staff_required
def products(r):
    form = ProductForm(r.POST or None, r.FILES or None)
    if r.method == 'POST' and form.is_valid():
        form.save(); messages.success(r, 'Product added.'); return redirect('products')
    return render(r, 'products.html', {'form': form, 'items': Product.objects.select_related('category')})

@staff_required
def product_edit(r, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(r.POST or None, r.FILES or None, instance=product)
    if r.method == 'POST' and form.is_valid():
        form.save(); messages.success(r, f'{product.name} updated.'); return redirect('products')
    return render(r, 'products.html', {
        'form': form, 'items': Product.objects.select_related('category'), 'editing': product,
    })

@staff_required
@require_POST
def product_delete(r, pk):
    try:
        get_object_or_404(Product, pk=pk).delete(); messages.success(r, 'Product deleted.')
    except ProtectedError:
        messages.error(r, 'This product has recorded sales, so it cannot be deleted.')
    return redirect('products')

def _loan_accounts(bound_payment=None, bound_customer_id=None):
    accounts = {}
    loan_sales = Sale.objects.filter(payment='loan', customer__isnull=False).select_related('customer', 'product')
    for sale in loan_sales:
        account = accounts.setdefault(sale.customer_id, {
            'customer': sale.customer, 'borrowed': Decimal('0.00'),
            'paid': Decimal('0.00'), 'items': [],
        })
        account['borrowed'] += sale.total
        account['items'].append(sale)
    for payment in LoanPayment.objects.select_related('customer'):
        account = accounts.get(payment.customer_id)
        if account:
            account['paid'] += payment.amount
    result = []
    for customer_id, account in accounts.items():
        account['balance'] = account['borrowed'] - account['paid']
        account['payment_form'] = (bound_payment if customer_id == bound_customer_id
                                   and bound_payment is not None
                                   else LoanPaymentForm(prefix=f'pay-{customer_id}')
                                   if account['balance'] > 0 else None)
        result.append(account)
    return sorted(result, key=lambda account: account['customer'].name.casefold())

@login_required
def sell(r):
    if r.method == 'POST' and r.POST.get('action') == 'loan_payment':
        customer = get_object_or_404(Customer, pk=r.POST.get('customer_id'))
        accounts = {a['customer'].pk: a for a in _loan_accounts()}
        account = accounts.get(customer.pk)
        payment_form = LoanPaymentForm(r.POST, prefix=f'pay-{customer.pk}')
        if account is None or account['balance'] <= 0:
            payment_form.add_error(None, 'This customer has no outstanding loan balance.')
        elif payment_form.is_valid():
            amount = payment_form.cleaned_data['amount']
            if amount > account['balance']:
                payment_form.add_error('amount', f'Payment cannot exceed the outstanding TSh {account["balance"]:,.2f}.')
            else:
                payment = payment_form.save(commit=False)
                payment.customer = customer
                payment.save()
                messages.success(r, f'Payment of TSh {amount:,.2f} recorded for {customer.name}.')
                return redirect('sell')
        form = SaleForm()
        return render(r, 'sell.html', {
            'form': form, 'recent': Sale.objects.select_related('product', 'customer')[:10],
            'loan_accounts': _loan_accounts(payment_form, customer.pk),
        })

    initial = None
    if r.method == 'GET' and r.GET.get('customer'):
        customer = get_object_or_404(Customer, pk=r.GET['customer'])
        initial = {'payment': 'loan', 'customer_name': customer.name}
    form = SaleForm(r.POST or None, initial=initial)
    if r.method == 'POST' and form.is_valid():
        sale = form.save()
        if sale.payment == 'loan':
            messages.success(r, f'Recorded {sale.quantity} x {sale.product.name} on loan for {sale.customer.name}.')
        else:
            messages.success(r, f'Sold {sale.quantity} x {sale.product.name} for TSh {sale.total:,.0f}.')
        return redirect('sell')
    return render(r, 'sell.html', {
        'form': form, 'recent': Sale.objects.select_related('product', 'customer')[:10],
        'loan_accounts': _loan_accounts(),
    })

@staff_required
def customers(r):
    form = CustomerForm(r.POST or None)
    if r.method == 'POST' and form.is_valid():
        form.save(); messages.success(r, 'Customer added.'); return redirect('customers')
    return render(r, 'customers.html', {'form': form, 'items': Customer.objects.all()})

@staff_required
def report(r):
    today = timezone.localdate()
    try:
        y, m = map(int, (r.GET.get('month') or today.strftime('%Y-%m')).split('-'))
    except ValueError:
        y, m = today.year, today.month
    sales = Sale.objects.filter(date__year=y, date__month=m).select_related('product')
    profit = sum(s.profit for s in sales)
    return render(r, 'report.html', {'month': f'{y}-{m:02d}', 'sales': sales,
        'revenue': sum(s.total for s in sales), 'profit': profit,
        'capital': profit * Decimal('0.7'), 'new_profit': profit * Decimal('0.3')})
