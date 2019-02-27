from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator


class PaymentMethod(models.Model):
    """
    Stores payment methods
    """
    class Meta:
        verbose_name="Moyen de paiement"
        verbose_name_plural = "Moyens de paiement"

    name = models.CharField(max_length=255, verbose_name="Nom")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_usable_in_cotisation = models.BooleanField(default=True, verbose_name="Cotisations ?")
    is_usable_in_reload = models.BooleanField(default=True, verbose_name="Rechargements ?")
    affect_balance = models.BooleanField(default=False, verbose_name="Affecte le solde")
    icon = models.CharField(max_length=255, verbose_name="Icône", blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class GeneralPreferences(models.Model):
    """
    Stores a unique line of general preferences
    """
    class Meta:
        verbose_name="Préférences générales"
        verbose_name_plural = "Préférences générales"

    is_active = models.BooleanField(default=True, verbose_name="Site actif")
    active_message = models.TextField(blank=True, verbose_name="Message non actif")
    global_message = models.TextField(blank=True, verbose_name="Message global")
    president = models.CharField(max_length=255, blank=True, verbose_name="Président")
    vice_president = models.CharField(max_length=255, blank=True, verbose_name="Vice Président")
    treasurer = models.CharField(max_length=255, blank=True, verbose_name="Trésorier")
    secretary = models.CharField(max_length=255, blank=True, verbose_name="Secrétaire")
    brewer = models.CharField(max_length=255, blank=True, verbose_name="Maître Brasseur")
    grocer = models.CharField(max_length=255, blank=True, verbose_name="Épic Épicier")
    use_pinte_monitoring = models.BooleanField(default=False, verbose_name="Suivi de pintes")
    lost_pintes_allowed = models.PositiveIntegerField(default=0, verbose_name="Nombre de pintes perdus admises")
    floating_buttons = models.BooleanField(default=False, verbose_name="Boutons flottants")
    home_text = models.TextField(blank=True, verbose_name="Message d'accueil")
    automatic_logout_time = models.PositiveIntegerField(null=True, verbose_name="Temps de déconnexion automatique")
    statutes = models.FileField(blank=True, null=True, verbose_name="Statuts")
    rules = models.FileField(blank=True, null=True, verbose_name="Règlement intérieur")
    menu = models.FileField(blank=True, null=True, verbose_name="Menu")
    history = HistoricalRecords()

class Cotisation(models.Model):
    """
    Stores cotisations
    """
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name="Montant", validators=[MinValueValidator(0)])
    duration = models.PositiveIntegerField(verbose_name="Durée de la cotisation (jours)")
    history = HistoricalRecords()

    def __str__(self):
        return "Cotisation de " + str(self.duration) + " jours pour le prix de " + str(self.amount) + "€"
