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
    Stores school.
    """
    class Meta:
        verbose_name = "École"

    name = models.CharField(max_length=255, verbose_name="Nom")
    """
    The name of the school
    """
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class CotisationHistory(models.Model):
    """
    Stores cotisation histories, related to :class:`preferences.models.Cotisation`.
    """
    class Meta:
        verbose_name = "Historique cotisation"
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Client")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Montant")
    """
    Price, in euros, of the cotisation.
    """
    duration = models.PositiveIntegerField(verbose_name="Durée")
    """
    Duration, in days, of the cotisation.
    """
    paymentDate = models.DateTimeField(auto_now_add=True, verbose_name="Date du paiement")
    """
    Date of the payment.
    """
    endDate = models.DateTimeField(verbose_name="Fin de la cotisation")
    """
    End date of the cotisation.
    """
    paymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, verbose_name="Moyen de paiement")
    """
    :class:`Payment method <preferences.models.PaymentMethod>` used.
    """
    cotisation = models.ForeignKey(Cotisation, on_delete=models.PROTECT, verbose_name="Type de cotisation")
    """
    :class:`~preferences.models.Cotisation` related.
    """
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="cotisation_made")
    """
    User (:class:`django.contrib.auth.models.User`) who registered the cotisation.
    """
    history = HistoricalRecords()

class WhiteListHistory(models.Model):
    """
    Stores whitelist history.
    """
    class Meta:
        verbose_name = "Historique accès gracieux"
        verbose_name_plural = "Historique accès gracieux"

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Client")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    paymentDate = models.DateTimeField(auto_now_add=True, verbose_name="Date de début")
    """
    Date of the beginning of the whitelist.
    """
    endDate = models.DateTimeField(verbose_name="Date de fin")
    """
    End date of the whitelist.
    """
    duration = models.PositiveIntegerField(verbose_name="Durée", help_text="Durée de l'accès gracieux en jour")
    """
    Duration, in days, of the whitelist
    """
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="whitelist_made")
    """
    User (:class:`django.contrib.auth.models.User`) who registered the cotisation.
    """
    history = HistoricalRecords()

class Profile(models.Model):
    """
    Stores user profile.
    """
    class Meta:
        verbose_name = "Profil"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    """
    Client (:class:`django.contrib.auth.models.User`).
    """
    credit = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="Crédit")
    """
    Amount of money, in euros, put on the account
    """
    debit = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="Débit")
    """
    Amount of money, in euros, spent form the account
    """
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=True, null=True, verbose_name="École")
    """
    :class:`~users.models.School` of the client
    """
    cotisationEnd = models.DateTimeField(blank=True, null=True, verbose_name="Fin de cotisation")
    """
    Date of end of cotisation for the client
    """
    history = HistoricalRecords()

    @property
    def is_adherent(self):
        """
        Test if a client is adherent.
        """
        if(self.cotisationEnd and self.cotisationEnd > timezone.now()):
            return True
        else:
            return False

    @property
    def balance(self):
        """
        Computes client balance (:attr:`gestion.models.Profile.credit` - :attr:`gestion.models.Profile.debit`).
        """
        return self.credit - self.debit

    def positiveBalance(self):
        """
        Test if the client balance is positive or null.
        """
        return self.balance >= 0

    @property
    def rank(self):
        """
        Computes the rank (by :attr:`gestion.models.Profile.debit`) of the client.
        """
        return Profile.objects.filter(debit__gte=self.debit).count()

    @property
    def alcohol(self):
        """
        Computes ingerated alcohol.
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
        Return the number of :class:`Pinte(s) <gestion.models.Pinte>` currently owned.
        """
        return self.user.pintes_owned_currently.count()

    def __str__(self):
        return str(self.user)

    def __getattr__(self, name):
        """
        Try to return the attribute and it doesn't exist, try to return the attribute of the associated user (:class:`django.contrib.auth.models.User`).
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
    Create profile when user (:class:`django.contrib.auth.models.User`) is created.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save profile when user (:class:`django.contrib.auth.models.User`) is saved.
    """
    instance.profile.save()

def str_user(self):
    """
    Rewrite str method for user (:class:`django.contrib.auth.models.User`).
    """
    if self.profile.is_adherent:
        fin = "Adhérent"
    else:
        fin = "Non adhérent"
    return self.username + " (" + self.first_name + " " + self.last_name + ", " + str(self.profile.balance) + "€, " + fin + ")" 


User.add_to_class("__str__", str_user)