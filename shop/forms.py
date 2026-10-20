from django import forms
from django.contrib.auth import get_user_model
from .models import Product, Customer, Sale, Category, Unit, LoanPayment

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name']

class ShopkeeperForm(forms.Form):
    name = forms.CharField(max_length=150, label='Shopkeeper name (used to sign in)')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        User = get_user_model()
        if User.objects.filter(username__iexact=name).exists():
            raise forms.ValidationError('A user with this name already exists.')
        return name

    def clean(self):
        data = super().clean()
        if data.get('password1') and data.get('password2') and data['password1'] != data['password2']:
            self.add_error('password2', 'The passwords do not match.')
        return data

    def save(self):
        User = get_user_model()
        name = self.cleaned_data['name']
        user = User.objects.create_user(username=name, password=self.cleaned_data['password1'], first_name=name)
        return user

class ProductForm(forms.ModelForm):
    unit = forms.ChoiceField(choices=())
    class Meta:
        model = Product
        fields = ['category', 'name', 'unit', 'quantity', 'buy_price', 'sell_price',
                  'items_per_carton', 'sell_carton_price', 'low_stock', 'expiry', 'image']
        widgets = {'expiry': forms.DateInput(attrs={'type': 'date'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['buy_price'].label = 'Buying price per single item (TSh)'
        self.fields['sell_price'].label = 'Selling price per single item (TSh)'
        self.fields['items_per_carton'].label = 'Single items in one carton'
        self.fields['items_per_carton'].help_text = 'Set the actual count for this product before entering a carton selling price.'
        self.fields['sell_carton_price'].label = 'Selling price per carton (TSh)'
        self.fields['sell_carton_price'].help_text = 'Optional. Leave blank if you do not sell this product by the carton.'
        choices = [(name, name) for name in Unit.objects.values_list('name', flat=True)]
        legacy = Product.objects.values_list('unit', flat=True).distinct()
        known = {choice[0] for choice in choices}
        choices.extend((value, value) for value in legacy if value not in known)
        if 'bottle' not in {choice[0] for choice in choices}:
            choices.append(('bottle', 'bottle'))
        self.fields['unit'].choices = choices

    def clean(self):
        cleaned = super().clean()
        carton_price = cleaned.get('sell_carton_price')
        items_per_carton = cleaned.get('items_per_carton')
        if carton_price is not None and items_per_carton is not None and items_per_carton < 2:
            self.add_error('items_per_carton', 'Enter the actual number of items in a carton before setting its price.')
        return cleaned

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

class SaleForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=100, required=False, label='Customer name')

    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'payment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['product', 'quantity', 'payment', 'customer_name'])
        self.fields['product'].label = 'Item to be purchased'
        self.fields['quantity'].label = 'Number of items'
        self.fields['payment'].label = 'Payment method'
        self.fields['customer_name'].widget.attrs.update({'autocomplete': 'name'})
        self.fields['product'].queryset = Product.objects.filter(quantity__gt=0).select_related('category')

    def clean(self):
        d = super().clean()
        p, q = d.get('product'), d.get('quantity')
        if p and q and q > p.quantity:
            raise forms.ValidationError(f'Only {p.quantity} {p.unit}(s) of {p.name} left in stock.')
        if d.get('payment') == 'loan' and not (d.get('customer_name') or '').strip():
            self.add_error('customer_name', 'Enter the customer name for a loan sale.')
        return d

    def save(self, commit=True):
        sale = super().save(commit=False)
        customer_name = (self.cleaned_data.get('customer_name') or '').strip()
        if sale.payment == 'loan':
            customer = Customer.objects.filter(name__iexact=customer_name).first()
            sale.customer = customer or Customer.objects.create(name=customer_name)
        if commit:
            sale.save()
            self.save_m2m()
        return sale

class LoanPaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01,
        label='Payment amount (TSh)',
    )

    class Meta:
        model = LoanPayment
        fields = ['amount', 'method']
        labels = {'method': 'Payment method'}
