from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator


class PaymentMethod(models.Model):
    """
    Stores payment methods
    """
    name = models.CharField(max_length=255, verbose_name="Nom")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_usable_in_cotisation = models.BooleanField(default=True, verbose_name="Cotisations ?")
    is_usable_in_reload = models.BooleanField(default=True, verbose_name="Rechargements ?")
    affect_balance = models.BooleanField(default=False, verbose_name="Affecte le solde")
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class GeneralPreferences(models.Model):
    """
    Stores a unique line of general preferences
    """
    is_active = models.BooleanField(default=True)
    active_message = models.TextField(blank=True)
    global_message = models.TextField(blank=True)
    president = models.CharField(max_length=255, blank=True)
    vice_president = models.CharField(max_length=255, blank=True)
    treasurer = models.CharField(max_length=255, blank=True)
    secretary = models.CharField(max_length=255, blank=True)
    brewer = models.CharField(max_length=255, blank=True)
    grocer = models.CharField(max_length=255, blank=True)
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
