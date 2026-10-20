from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=60)
    class Meta: verbose_name_plural = 'categories'
    def __str__(self): return self.name

class Unit(models.Model):
    name = models.CharField(max_length=20, unique=True)
    class Meta: ordering = ['name']
    def __str__(self): return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default='bottle')
    quantity = models.PositiveIntegerField(default=0)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    items_per_carton = models.PositiveIntegerField(default=1, help_text='Number of single items in one carton')
    sell_carton_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Leave blank if this product is not sold by the carton')
    expiry = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='products', blank=True)
    low_stock = models.PositiveIntegerField(default=10, help_text='Warn when stock falls to this number')
    class Meta: ordering = ['category', 'name']
    @property
    def low(self): return self.quantity <= self.low_stock
    @property
    def profit_each(self): return self.sell_price - self.buy_price
    @property
    def carton_buy_cost(self): return self.buy_price * self.items_per_carton
    @property
    def carton_profit(self):
        if self.sell_carton_price is None: return None
        return self.sell_carton_price - self.carton_buy_cost
    def __str__(self): return f'{self.name} ({self.unit})'

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=80, blank=True)
    def __str__(self): return self.name

class Sale(models.Model):
    PAY = [('cash', 'Cash'), ('mobile', 'Mobile money'), ('bank', 'Bank'), ('loan', 'Loan')]
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    payment = models.CharField(max_length=10, choices=PAY, default='cash')
    location = models.CharField(max_length=80, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-date']
    @property
    def total(self): return self.unit_price * self.quantity
    @property
    def profit(self): return (self.unit_price - self.unit_cost) * self.quantity
    def save(self, *a, **k):
        if not self.pk:
            self.unit_price, self.unit_cost = self.product.sell_price, self.product.buy_price
            self.product.quantity -= self.quantity
            self.product.save()
        super().save(*a, **k)

class LoanPayment(models.Model):
    METHODS = [('cash', 'Cash'), ('mobile', 'Mobile money'), ('bank', 'Bank')]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='loan_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS, default='cash')
    date = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-date']
    def __str__(self): return f'{self.customer.name}: TSh {self.amount}'
