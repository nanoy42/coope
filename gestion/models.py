from django.db import models
from django.contrib.auth.models import User
from preferences.models import PaymentMethod
class Product(models.Model):
    P_PRESSION = 'PP'
    D_PRESSION = 'DP'
    G_PRESSION = 'GP'
    BOTTLE = 'BT'
    SOFT = 'SO'
    FOOD = 'FO'
    TYPEINPUT_CHOICES_CATEGORIE = (
        (P_PRESSION, "Pinte Pression"),
        (D_PRESSION, "Demi Pression"),
        (G_PRESSION, "Galopin pression"),
        (BOTTLE, "Bouteille"),
        (SOFT, "Soft"),
        (FOOD, "Bouffe"),
    )
    name = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    stockHold = models.IntegerField(default=0)
    stockBar = models.IntegerField(default=0)
    barcode= models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=2, choices=TYPEINPUT_CHOICES_CATEGORIE, default=FOOD)
    needQuantityButton = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_beer = models.BooleanField(default=False)
    volume = models.IntegerField(default=0)
    deg = models.DecimalField(default=0,max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nom


def isPinte(id):
    product = Product.objects.get(id=id)
    if product.category != Product.P_PRESSION:
        raise ValidationError(
            ('%(product)s n\'est pas une pinte'),
            params={'product': product},
        )


def isDemi(id):
    product = Product.objects.get(id=id)
    if produit.category != Product.D_PRESSION:
        raise ValidationError(
            ('%(product)s n\'est pas un demi'),
            params={'product': product},
        )

def isGalopin(id):
    product = Product.objects.get(id)
    if product.category != Product.G_PRESSION:
        raise ValidationError(
            ('%(product)s n\'est pas un galopin'),
            params={'product': product},
        )

class Barrel(models.Model):
    name = models.CharField(max_length=20)
    stockHold = models.IntegerField(default=0)
    barcode = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    capacity = models.IntegerField(default=30)
    pinte = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futp", validators=[isPinte])
    demi = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futd", validators=[isDemi])
    galopin = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futg", validators=[isGalopin],null=True, blank=True)
    active= models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Reload(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reload_taken")
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    PaymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reload_realized")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Rechargement effectue par {0} le {1} ({2} euros, coopeman : {3})".format(self.customer, self.date, self.amount, self.coopeman)


class Raming(models.Model):
    barrel = models.ForeignKey(Barrel, on_delete=models.PROTECT)
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Percussion d'un {0} effectué par {1} le {2}".format(self.barrel, self.coopeman, self.date)

class Stocking(models.Model):
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Inventaire fait le {0}".format(self.date)


class Refund(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cutsomer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="refund_taken")
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="refund_realized")

    def __str__(self):
        return "{0} remboursé de {1} le {2} (effectué par {3})".format(self.customer, self.amount, self.date, self.coopeman)


class Menu(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    barcode = models.CharField(max_length=20, unique=True)
    articles = models.ManyToManyField(Product)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class MenuHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="menu_taken")
    quantity = models.PositiveIntegerField(default=0)
    PaymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="menu_selled")

    def __str__(self):
        return "{2} a consommé {0} {1}".format(self.quantite, self.menu, self.client)

class ConsumptionHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consumption_taken")
    quantity = models.PositiveIntegerField(default=0)
    paymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    menu = models.ForeignKey(MenuHistory, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consumption_selled")

    def __str__(self):
        return "{0} {1} consommé par {2} le {3} (encaissé par {4})".format(self.quantity, self.product, self.customer, self.date, self.coopeman)
