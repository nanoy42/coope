from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords
from preferences.models import PaymentMethod, Cotisation
from gestion.models import ConsumptionHistory

class School(models.Model):
    """
    Stores school
    """
    class Meta:
        verbose_name = "École"

    name = models.CharField(max_length=255, verbose_name="Nom")
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class CotisationHistory(models.Model):
    """
    Stores cotisations history, related to :model:`preferences.Cotisation`
    """
    class Meta:
        verbose_name = "Historique cotisation"
        permissions = (
            ("validate_cotisationhistory", "Peut (in)valider les cotisations"),
        )

    WAITING = 0
    VALID = 1
    INVALID = 2
    VALIDATION_CHOICES = (
        (WAITING, 'En attente de validation'),
        (VALID, 'Validée'),
        (INVALID, 'Invalidée'),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Client")
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Montant")
    duration = models.PositiveIntegerField(verbose_name="Durée")
    paymentDate = models.DateTimeField(auto_now_add=True, verbose_name="Date du paiement")
    endDate = models.DateTimeField(verbose_name="Fin de la cotisation")
    paymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Moyen de paiement")
    cotisation = models.ForeignKey(Cotisation, on_delete=models.PROTECT, verbose_name="Type de cotisation")
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="cotisation_made")
    valid = models.IntegerField(choices=VALIDATION_CHOICES, default=WAITING)
    history = HistoricalRecords()

class WhiteListHistory(models.Model):
    """
    Stores whitelist history
    """
    class Meta:
        verbose_name = "Historique accès gracieux"

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    paymentDate = models.DateTimeField(auto_now_add=True)
    endDate = models.DateTimeField()
    duration = models.PositiveIntegerField(verbose_name="Durée", help_text="Durée de l'accès gracieux en jour")
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="whitelist_made")
    history = HistoricalRecords()

class Profile(models.Model):
    """
    Stores user profile
    """
    class Meta:
        verbose_name = "Profil"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=True, null=True)
    cotisationEnd = models.DateTimeField(blank=True, null=True)
    date_verified = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()

    @property
    def is_verified(self):
        """
        Test if a user is verified
        """
        return self.date_verified is not None

    @property
    def is_adherent(self):
        """
        Test if a user is adherent
        """
        if(self.is_verified and self.cotisationEnd and self.cotisationEnd > timezone.now()):
            return True
        else:
            return False

    @property
    def balance(self):
        """
        Computes user balance
        """
        return self.credit - self.debit

    def positiveBalance(self):
        """
        Test if the user balance is positive or null
        """
        return self.balance >= 0

    @property
    def rank(self):
        """
        Computes the rank (by debit) of the user
        """
        return Profile.objects.filter(debit__gte=self.debit).count()

    @property
    def alcohol(self):
        """
        Computes ingerated alcohol
        """
        consumptions = ConsumptionHistory.objects.filter(customer=self.user).select_related('product')
        alcohol = 0
        for consumption in consumptions:
            product = consumption.product
            alcohol += consumption.quantity * float(product.deg) * product.volume * 0.79 /10 /1000
        return alcohol

    @property
    def nb_pintes(self):
        """
        Return the number of pintes currently owned
        """
        return self.user.pintes_owned_currently.count()

    def __str__(self):
        return str(self.user)

    def __getattr__(self, name):
        """
        Tente de retourner l'attribut de l'instance et si l'attribut n'existe pas,
        tente de retourner l'attribut de l'user associé à l'instance
        """
        try:
            r = self.__getattribute__(name)
        except AttributeError:
            try:
                r = super().__getattr__(name)
            except AttributeError:
                r = getattr(self.user, name)
        return r


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create profile when user is created
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save profile when user is saved
    """
    instance.profile.save()

def str_user(self):
    """
    Rewrite str method for user
    """
    if self.profile.is_adherent:
        fin = "Adhérent"
    else:
        fin = "Non adhérent"
    return self.username + " (" + self.first_name + " " + self.last_name + ", " + str(self.profile.balance) + "€, " + fin + ")" 


User.add_to_class("__str__", str_user)