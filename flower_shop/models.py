from datetime import timezone
from django.db import models
import re
from django.core.validators import MinValueValidator, MaxValueValidator

class AddressMixin:
    def _parse_address(self):
        if not self.address:
            return ["", "", "", ""]
        return re.sub(r'^\(|\)$', '', self.address).split(',')

    def _format_address(self, parts):
        return f'({",".join(str(p) for p in parts)})'

    @property
    def city(self):
        return self._parse_address()[0]

    @city.setter
    def city(self, value):
        parts = self._parse_address()
        parts[0] = value
        self.address = self._format_address(parts)

    @property
    def street(self):
        return self._parse_address()[1]

    @street.setter
    def street(self, value):
        parts = self._parse_address()
        parts[1] = value
        self.address = self._format_address(parts)

    @property
    def house(self):
        return self._parse_address()[2]

    @house.setter
    def house(self, value):
        parts = self._parse_address()
        parts[2] = str(value)
        self.address = self._format_address(parts)

    @property
    def flat(self):
        return self._parse_address()[3]

    @flat.setter
    def flat(self, value):
        parts = self._parse_address()
        parts[3] = str(value)
        self.address = self._format_address(parts)

class FullNameMixin:
    composite_field_name = 'cour_name'  # або 'cust_name'

    def _parse_composite(self):
        value = getattr(self, self.composite_field_name, "")
        if not value:
            return ["", "", ""]
        return re.sub(r'^\(|\)$', '', value).split(',')

    def _format_composite(self, parts):
        return f'({",".join(parts)})'

    @property
    def first_name(self):
        return self._parse_composite()[0]

    @first_name.setter
    def first_name(self, value):
        parts = self._parse_composite()
        parts[0] = value
        setattr(self, self.composite_field_name, self._format_composite(parts))

    @property
    def surname(self):
        return self._parse_composite()[1]

    @surname.setter
    def surname(self, value):
        parts = self._parse_composite()
        parts[1] = value
        setattr(self, self.composite_field_name, self._format_composite(parts))

    @property
    def middle_name(self):
        return self._parse_composite()[2]

    @middle_name.setter
    def middle_name(self, value):
        parts = self._parse_composite()
        parts[2] = value
        setattr(self, self.composite_field_name, self._format_composite(parts))


class Couriers(FullNameMixin, models.Model):
    kod = models.AutoField(primary_key=True)
    cour_name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    phone_number = models.CharField(unique=True, max_length=20)

    composite_field_name = 'cour_name'

    class Meta:
        managed = False
        db_table = 'couriers'

    def __str__(self):
        return f"{self.first_name} {self.surname}"

class Customers(FullNameMixin, AddressMixin, models.Model):
    kod = models.AutoField(primary_key=True)
    cust_name = models.CharField(max_length=255)
    phone_number = models.CharField(unique=True, max_length=20)
    email = models.CharField(unique=True, max_length=255)
    address = models.CharField(max_length=255)
    photo_link = models.TextField(blank=True, null=True)

    composite_field_name = 'cust_name'

    class Meta:
        managed = False
        db_table = 'customers'
    
    def __str__(self):
        return f"{self.first_name} {self.surname} {self.middle_name}, {self.phone_number}, {self.email}, ({self.city}, {self.street}, {self.house}, {self.flat})"

class Orders(models.Model):
    DELIVERY_CHOICES = [
        ('самовивіз', 'Самовивіз'),
        ('кур’єр', 'Кур’єр'),
        ('пошта', 'Пошта'),
    ]

    STATUS_CHOICES = [
        ('створено', 'Створено'),
        ('в дорозі', 'В дорозі'),
        ('доставлено', 'Доставлено'),
        ('не доставлено', 'Не доставлено'),
        ('відмінено', 'Відмінено'),
    ]

    o_kod = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customers, models.DO_NOTHING, db_column='customer')
    order_date = models.DateField(editable=False, default=timezone.now)
    delivery_date = models.DateField()
    delivery_method = models.CharField(
        max_length=30,
        choices=DELIVERY_CHOICES,
        default='кур’єр'
    )
    courier_id = models.ForeignKey(Couriers, models.DO_NOTHING, blank=True, null=True, db_column='courier_id')
    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='створено'
    )

    class Meta:
        managed = False
        db_table = 'orders'
    
    def __str__(self):
        return f"Замовлення #{self.o_kod} — Статус: {self.order_status}"

class Genera(models.Model):
    g_kod = models.AutoField(primary_key=True)
    genus_name = models.CharField(unique=True, max_length=30)

    class Meta:
        managed = False
        db_table = 'genera'

    def __str__(self):
        return self.genus_name

class Species(models.Model):
    s_kod = models.AutoField(primary_key=True)
    species_name = models.CharField(max_length=30)
    genus = models.ForeignKey(Genera, models.DO_NOTHING, db_column='genus')
    instruction = models.CharField(max_length=500, default='No instructions')
    storage_period = models.SmallIntegerField()
    photo_link = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'species'
    
    def __str__(self):
        return f"{self.species_name} ({self.genus.genus_name})"

class Planted(models.Model):
    p_kod = models.AutoField(primary_key=True)
    flower = models.ForeignKey(Species, models.DO_NOTHING, db_column='flower')
    planting_day = models.DateField(editable=False, default=timezone.now)
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Кількість має бути більше нуля."),
            MaxValueValidator(9999, message="Кількість має бути меншою за 10 000.")
        ]
    )

    class Meta:
        managed = False
        db_table = 'planted'
    
    def __str__(self):
        return f"Посаджено {self.amount} квіток ({self.flower.species_name}) на {self.planting_day}"

class DefectiveProduct(models.Model):
    kod = models.AutoField(primary_key=True)
    flower = models.ForeignKey(Planted, on_delete=models.CASCADE, db_column='flower')
    write_off_date = models.DateField(editable=False, default=timezone.now)
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Кількість має бути більше нуля.")
        ]
    )

    class Meta:
        managed = False
        db_table = 'defective_product'
    
    def __str__(self):
        return f"Списано {self.amount} ({self.flower}) — {self.write_off_date}"

class Product(models.Model):
    kod = models.AutoField(primary_key=True)
    flower = models.ForeignKey(Planted, models.DO_NOTHING, db_column='flower')
    availability_date = models.DateField(editable=False, default=timezone.now)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, message="Ціна має бути більшою за 0."),
            MaxValueValidator(99999.99, message="Ціна має бути меншою за 100000.")
        ],
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'product'
        unique_together = (('flower', 'availability_date'),)

    def __str__(self):
        return f"Товар: {self.flower} | Ціна: {self.price} грн"

class Fertilizers(models.Model):
    fe_kod = models.AutoField(primary_key=True)
    fertilizer_name = models.CharField(unique=True, max_length=30)

    class Meta:
        managed = False
        db_table = 'fertilizers'
    
    def __str__(self):
        return self.fertilizer_name

class GenusFertilizer(models.Model):
    kod = models.AutoField(primary_key=True)
    genus = models.ForeignKey(Genera, models.DO_NOTHING, db_column='genus')
    fertilizer = models.ForeignKey(Fertilizers, models.DO_NOTHING, db_column='fertilizer')

    class Meta:
        managed = False
        db_table = 'genus_fertilizer'
    
    def __str__(self):
        return f"{self.genus.genus_name} — {self.fertilizer.fertilizer_name}"

class Suppliers(AddressMixin, models.Model):
    s_kod = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'suppliers'
    
    def __str__(self):
        return f"{self.supplier_name} ({self.address}, {self.phone_number})"

class OrderedFertilizers(models.Model):
    fertilizer_id = models.ForeignKey(Fertilizers, models.DO_NOTHING, db_column='fertilizer_id')
    supplier_id = models.ForeignKey(Suppliers, models.DO_NOTHING, db_column='supplier_id')
    date_of_purchase = models.DateField(editable=False, default=timezone.now)
    amount = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(99999)
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[
        MinValueValidator(0.01),
        MaxValueValidator(99999.99)
    ])

    class Meta:
        managed = False
        db_table = 'ordered_fertilizers'
        unique_together = (('fertilizer_id', 'supplier_id', 'date_of_purchase'),)
    
    def __str__(self):
        return f"{self.fertilizer_id.fertilizer_name} від {self.supplier_id.supplier_name} — {self.date_of_purchase}"

class UsedFertilizers(models.Model):
    genus_fertilizer_id = models.ForeignKey(GenusFertilizer, models.DO_NOTHING, db_column='genus_fertilizer_id')
    use_date = models.DateField(editable=False, default=timezone.now)
    amount = models.IntegerField(validators=[
        MinValueValidator(1, message="Кількість має бути більшою за 0.")
    ])

    class Meta:
        managed = False
        db_table = 'used_fertilizers'
        unique_together = (('genus_fertilizer_id', 'use_date'),)
    
    def __str__(self):
        return f"{self.genus_fertilizer_id} — {self.use_date} — {self.amount}"

class OrderItems(models.Model):
    kod = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id')
    flower = models.ForeignKey(Species, models.DO_NOTHING, db_column='flower')
    amount = models.IntegerField(validators=[
        MinValueValidator(1, message="Кількість має бути більшою за 0.")
    ])

    class Meta:
        managed = False
        db_table = 'order_items'
        unique_together = (('order_id', 'flower'),)
    
    def __str__(self):
        return f"Замовлення #{self.order_id.o_kod} — {self.flower.species_name} — Кількість: {self.amount}"

class ProductOrderItems(models.Model):
    product = models.ForeignKey(Product, models.DO_NOTHING, db_column='product')
    order_item = models.ForeignKey(OrderItems, models.DO_NOTHING, db_column='order_item')
    amount = models.IntegerField(validators=[
        MinValueValidator(1, message="Кількість має бути більшою за 0."),
        MaxValueValidator(99999, message="Кількість має бути меншою за 100 000.")
    ])

    class Meta:
        managed = False
        db_table = 'product_order_items'
        unique_together = (('product', 'order_item'),)
    
    def __str__(self):
        return f"{self.amount} одиниць з партії #{self.product.kod} у позиції #{self.order_item.kod}"



