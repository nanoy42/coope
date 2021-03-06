from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator
from preferences.models import PaymentMethod
from django.core.exceptions import ValidationError

class Category(models.Model):
    """
    A product category
    """
    class Meta:
        verbose_name="Catégorie"
    name = models.CharField(max_length=100, verbose_name="Nom", unique=True)
    order = models.IntegerField(default=0)
    """
    The name of the category
    """

    def __str__(self):
        return self.name

    @property
    def active_products(self):
        """
        Return active producs of this category
        """
        return self.product_set.filter(is_active=True)
    
    @property
    def active_stock_products(self):
        """
        Return active products that use stocks
        """
        return self.product_set.filter(is_active=True).filter(use_stocks=True)

class Product(models.Model):
    """
    Stores a product.
    """
    DRAFT_NONE = 0
    DRAFT_PINTE = 1
    DRAFT_DEMI = 2
    DRAFT_GALOPIN = 3

    DRAFT_TYPES = (
        (DRAFT_NONE, "Pas une bière pression"),
        (DRAFT_PINTE, "Pinte"),
        (DRAFT_DEMI, "Demi"),
        (DRAFT_GALOPIN, "Galopin"),
    )

    class Meta:
        verbose_name = "Produit"

    name = models.CharField(max_length=255, verbose_name="Nom", unique=True)
    """
    The name of the product.
    """
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Prix de vente", validators=[MinValueValidator(0)])
    """
    The price of the product.
    """
    stock = models.IntegerField(default=0, verbose_name="Stock")
    """
    Number of product
    """
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name="Catégorie")
    """
    The category of the product
    """
    needQuantityButton = models.BooleanField(default=False, verbose_name="Bouton quantité")
    """
    If True, a javascript quantity button will be displayed
    """
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    """
    If True, will be displayed on the :func:`gestion.views.manage` view.
    """
    volume = models.PositiveIntegerField(default=0)
    """
    The volume, if relevant, of the product
    """
    deg = models.DecimalField(default=0,max_digits=5, decimal_places=2, verbose_name="Degré", validators=[MinValueValidator(0)])
    """
    Degree of alcohol, if relevant
    """
    adherentRequired = models.BooleanField(default=True, verbose_name="Adhérent requis")
    """
    If True, only adherents will be able to buy this product
    """
    showingMultiplier = models.PositiveIntegerField(default=1)
    """
    On the graphs on :func:`users.views.profile` view, the number of total consumptions is divised by the showingMultiplier
    """
    draft_category = models.IntegerField(choices=DRAFT_TYPES, default=DRAFT_NONE, verbose_name="Type de pression")
    use_stocks = models.BooleanField(default=True, verbose_name="Utiliser les stocks ?")
    history = HistoricalRecords()

    def __str__(self):
        if self.draft_category == self.DRAFT_NONE:
            return self.name + " (" + str(self.amount) + " €)"
        else:
            return self.name + " (" + str(self.amount) + " €, " + str(self.deg) + "°)"


    def user_ranking(self, pk):
        """
        Return the user ranking for the product
        """
        user = User.objects.get(pk=pk)
        consumptions = Consumption.objects.filter(customer=user).filter(product=self)
        if consumptions:
            return (user, consumptions[0].quantity)
        else:
            return (user, 0)

    @property
    def ranking(self):
        """
        Get the first 25 users with :func:`~gestion.models.user_ranking`
        """
        users = User.objects.all()
        ranking = [self.user_ranking(user.pk) for user in users]
        ranking.sort(key=lambda x:x[1], reverse=True)
        return ranking[0:25]


def isPinte(id):
    product = Product.objects.get(id=id)
    if product.draft_category != Product.DRAFT_PINTE:
        raise ValidationError(
            ('%(product)s n\'est pas une pinte'),
            params={'product': product},
        )


def isDemi(id):
    product = Product.objects.get(id=id)
    if product.draft_category != Product.DRAFT_DEMI:
        raise ValidationError(
            ('%(product)s n\'est pas un demi'),
            params={'product': product},
        )

def isGalopin(id):
    product = Product.objects.get(id=id)
    if product.draft_category != Product.DRAFT_GALOPIN:
        raise ValidationError(
            ('%(product)s n\'est pas un galopin'),
            params={'product': product},
        )

class Keg(models.Model):
    """
    Stores a keg.
    """
    class Meta:
        verbose_name = "Fût"
        permissions = (
            ("open_keg", "Peut percuter les fûts"),
            ("close_keg", "Peut fermer les fûts")
        )

    name = models.CharField(max_length=255, unique=True, verbose_name="Nom")
    """
    The name of the keg.
    """
    stockHold = models.IntegerField(default=0, verbose_name="Stock en soute")
    """
    The number of this keg in the hold.
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Prix du fût", validators=[MinValueValidator(0)])
    """
    The price of the keg.
    """
    capacity = models.IntegerField(default=30, verbose_name="Capacité (L)")
    """
    The capacity, in liters, of the keg.
    """
    pinte = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futp", validators=[isPinte])
    """
    The related :class:`~gestion.models.Product` for pint.
    """
    demi = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futd", validators=[isDemi])
    """
    The related :class:`~gestion.models.Product` for demi.
    """
    galopin = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="futg", validators=[isGalopin],null=True, blank=True)
    """
    The related :class:`~gestion.models.Product` for galopin.
    """
    is_active = models.BooleanField(default=False, verbose_name="Actif")
    """
    If True, will be displayed on :func:`~gestion.views.manage` view
    """
    deg = models.DecimalField(default=0,max_digits=5, decimal_places=2, verbose_name="Degré", validators=[MinValueValidator(0)])
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class KegHistory(models.Model):
    """
    Stores a keg history, related to :class:`~gestion.models.Keg`.
    """
    class Meta:
        verbose_name = "Historique de fût"

    keg = models.ForeignKey(Keg, on_delete=models.PROTECT, verbose_name="Fût")
    """
    The :class:`~gestion.models.Keg` instance.
    """
    openingDate = models.DateTimeField(auto_now_add=True, verbose_name="Date ouverture")
    """
    The date when the keg was opened.
    """
    quantitySold = models.DecimalField(decimal_places=2, max_digits=5, default=0, verbose_name="Quantité vendue")
    """
    The quantity, in liters, sold.
    """
    amountSold = models.DecimalField(decimal_places=2, max_digits=5, default=0, verbose_name="Somme vendue")
    """
    The quantity, in euros, sold.
    """
    closingDate = models.DateTimeField(null=True, blank=True, verbose_name="Date fermeture")
    """
    The date when the keg was closed
    """
    isCurrentKegHistory = models.BooleanField(default=True, verbose_name="Actuel")
    """
    If True, it corresponds to the current Keg history of :class:`~gestion.models.Keg` instance.
    """
    history = HistoricalRecords()

    def __str__(self):
        res = "Fût de " + str(self.keg) + " (" + str(self.openingDate) + " - "
        if(self.closingDate):
            res += str(self.closingDate) + ")"
        else:
            res += "?)"
        return res

class Reload(models.Model):
    """
    Stores reloads.
    """
    class Meta:
        verbose_name = "Rechargement"
    
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reload_taken", verbose_name="Client")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Montant", validators=[MinValueValidator(0)])
    """
    Amount of the reload.
    """
    PaymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Moyen de paiement")
    """
    :class:`Payment Method <preferences.models.PaymentMethod>` of the reload.
    """
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reload_realized")
    """
    Coopeman (:class:`django.contrib.auth.models.User`) who collected the reload.
    """
    date = models.DateTimeField(auto_now_add=True)
    """
    Date of the reload.
    """
    history = HistoricalRecords()

    def __str__(self):
        return "Rechargement effectue par {0} le {1} ({2} euros, coopeman : {3})".format(self.customer, self.date, self.amount, self.coopeman)

class Refund(models.Model):
    """
    Stores refunds.
    """
    class Meta:
        verbose_name = "Remboursement"

    date = models.DateTimeField(auto_now_add=True)
    """
    Date of the refund
    """
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="refund_taken", verbose_name="Client")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Montant", validators=[MinValueValidator(0)])
    """
    Amount of the refund.
    """
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="refund_realized")
    """
    Coopeman (:class:`django.contrib.auth.models.User`) who realized the refund.
    """
    history = HistoricalRecords()

    def __str__(self):
        return "{0} remboursé de {1} le {2} (effectué par {3})".format(self.customer, self.amount, self.date, self.coopeman)


class Menu(models.Model):
    """
    Stores menus.
    """
    name = models.CharField(max_length=255, verbose_name="Nom")
    """
    Name of the menu.
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Montant", validators=[MinValueValidator(0)])
    """
    Price of the menu.
    """
    articles = models.ManyToManyField(Product, verbose_name="Produits")
    """
    Stores :class:`Products <gestion.models.Product>` contained in the menu
    """
    is_active = models.BooleanField(default=False, verbose_name="Actif")
    """
    If True, the menu will be displayed on the :func:`gestion.views.manage` view
    """
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    @property
    def adherent_required(self):
        """
        Test if the menu contains a restricted :class:`~gestion.models.Product`
        """
        res = False
        for article in self.articles.all():
            res = res or article.adherentRequired
        return res

class MenuHistory(models.Model):
    """
    Stores MenuHistory related to :class:`~gestion.models.Menu`.
    """
    class Meta:
        verbose_name = "Historique de menu"

    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="menu_taken", verbose_name="Client")

    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    paymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Moyen de paiement")
    """
    :class:`Payment Method <preferences.models.PaymentMethod>` of the Menu purchased.
    """
    date = models.DateTimeField(auto_now_add=True)
    """
    Date of the purhcase.
    """
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    """
    :class:`gestion.models.Menu` purchased.
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="Montant")
    """
    Price of the purchase.
    """
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="menu_selled")
    """
    Coopeman (:class:django.contrib.auth.models.User`) who collected the money.
    """
    history = HistoricalRecords()

    def __str__(self):
        return "{2} a consommé {0} {1}".format(self.quantity, self.menu, self.customer)

class ConsumptionHistory(models.Model):
    """
    Stores consumption history related to Product
    """
    class Meta:
        verbose_name = "Consommation"

    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consumption_taken", verbose_name="Client")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité")
    """
    Quantity of :attr:`gestion.models.ConsumptionHistory.product` taken.
    """
    paymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Moyen de paiement")
    """
    :class:`Payment Method <preferences.models.PaymentMethod>` of the product purchased.
    """
    date = models.DateTimeField(auto_now_add=True)
    """
    Date of the purhcase.
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Produit")
    """
    :class:`gestion.models.product` purchased.
    """
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="Montant")
    """
    Price of the purchase.
    """
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consumption_selled")
    """
    Coopeman (:class:django.contrib.auth.models.User`) who collected the money.
    """
    history = HistoricalRecords()

    def __str__(self):
        return "{0} {1} consommé par {2} le {3} (encaissé par {4})".format(self.quantity, self.product, self.customer, self.date, self.coopeman)

class Consumption(models.Model):
    """
    Stores total consumptions.
    """
    class Meta:
        verbose_name = "Consommation totale"

    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consumption_global_taken", verbose_name="Client")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Produit")
    """
    A :class:`gestion.models.Product` instance.
    """
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité")
    """
    The total number of :attr:`gestion.models.Consumption.product` consumed by the :attr:`gestion.models.Consumption.consumer`.
    """
    history = HistoricalRecords()

    def __str__(self):
        return "Consommation de " + str(self.customer) + " concernant le produit " + str(self.product)

class Pinte(models.Model):
    """
    Stores a physical pinte
    """
    current_owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None, related_name="pintes_owned_currently")
    """
    The current owner (:class:`django.contrib.auth.models.User`).
    """
    previous_owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None, related_name="pintes_owned_previously")
    """
    The previous owner (:class:`django.contrib.auth.models.User`).
    """
    last_update_date = models.DateTimeField(auto_now=True)
    """
    The last update date
    """
    history = HistoricalRecords()
