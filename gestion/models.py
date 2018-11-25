from django.db import models
from django.contrib.auth.models import User
from preferences.models import PaymentMethod
from django.core.exceptions import ValidationError

class Product(models.Model):
    P_PRESSION = 'PP'
    D_PRESSION = 'DP'
    G_PRESSION = 'GP'
    BOTTLE = 'BT'
    SOFT = 'SO'
    FOOD = 'FO'
    PANINI = 'PA'
    TYPEINPUT_CHOICES_CATEGORIE = (
        (P_PRESSION, "Pinte Pression"),
        (D_PRESSION, "Demi Pression"),
        (G_PRESSION, "Galopin pression"),
        (BOTTLE, "Bouteille"),
        (SOFT, "Soft"),
        (FOOD, "Bouffe autre que panini"),
        (PANINI, "Bouffe pour panini"),
    )
    name = models.CharField(max_length=40, verbose_name="Nom", unique=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Prix de vente")
    stockHold = models.IntegerField(default=0, verbose_name="Stock en soute")
    stockBar = models.IntegerField(default=0, verbose_name="Stock en bar")
    barcode= models.CharField(max_length=20, unique=True, verbose_name="Code barre")
    category = models.CharField(max_length=2, choices=TYPEINPUT_CHOICES_CATEGORIE, default=FOOD, verbose_name="Catégorie")
    needQuantityButton = models.BooleanField(default=False, verbose_name="Bouton quantité")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    volume = models.IntegerField(default=0)
    deg = models.DecimalField(default=0,max_digits=5, decimal_places=2, verbose_name="Degré")
    adherentRequired = models.BooleanField(default=True)

    def __str__(self):
        return self.name


def isPinte(id):
    product = Product.objects.get(id=id)
    if product.category != Product.P_PRESSION:
        raise ValidationError(
            ('%(product)s n\'est pas une pinte'),
            params={'product': product},
        )


def isDemi(id):
    product = Product.objects.get(id=id)
    if product.category != Product.D_PRESSION:
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

class Keg(models.Model):
    class Meta:
        permissions = (
            ("open_keg", "Peut percuter les fûts"),
            ("close_keg", "Peut fermer les fûts")
        )

    name = models.CharField(max_length=20, unique=True, verbose_name="Nom")
    stockHold = models.IntegerField(default=0, verbose_name="Stock en soute")
    barcode = models.CharField(max_length=20, unique=True, verbose_name="Code barre")
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Prix du fût")
    capacity = models.IntegerField(default=30, verbose_name="Capacité (L)")
    pinte = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futp", validators=[isPinte])
    demi = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futd", validators=[isDemi])
    galopin = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futg", validators=[isGalopin],null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Actif")

    def __str__(self):
        return self.name

class KegHistory(models.Model):
    keg = models.ForeignKey(Keg, on_delete=models.PROTECT)
    openingDate = models.DateTimeField(auto_now_add=True)
    quantitySold = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    amountSold = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    closingDate = models.DateTimeField(null=True, blank=True)
    isCurrentKegHistory = models.BooleanField(default=True)

    def __str__(self):
        res = "Fût de " + str(self.keg) + " (" + str(self.openingDate) + " - "
        if(self.closingDate):
            res += str(self.closingDate) + ")"
        else:
            res += "?)"
        return res

class Reload(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reload_taken", verbose_name="Client")
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Montant")
    PaymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Moyen de paiement")
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reload_realized")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Rechargement effectue par {0} le {1} ({2} euros, coopeman : {3})".format(self.customer, self.date, self.amount, self.coopeman)


class Raming(models.Model):
    keg = models.ForeignKey(Keg, on_delete=models.PROTECT)
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Percussion d'un {0} effectué par {1} le {2}".format(self.keg, self.coopeman, self.date)

class Stocking(models.Model):
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Inventaire fait le {0}".format(self.date)


class Refund(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="refund_taken", verbose_name="Client")
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Montant")
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="refund_realized")

    def __str__(self):
        return "{0} remboursé de {1} le {2} (effectué par {3})".format(self.customer, self.amount, self.date, self.coopeman)


class Menu(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Montant")
    barcode = models.CharField(max_length=20, unique=True, verbose_name="Code barre")
    articles = models.ManyToManyField(Product, verbose_name="Produits")
    is_active = models.BooleanField(default=False, verbose_name="Actif")

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
        return "{2} a consommé {0} {1}".format(self.quantity, self.menu, self.customer)

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

class Consumption(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consumption_global_taken")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Consommation de " + str(self.customer) + " concernant le produit " + str(self.product)
