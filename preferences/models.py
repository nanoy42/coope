from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator


class PaymentMethod(models.Model):
    """
    Stores payment methods.
    """
    class Meta:
        verbose_name="Moyen de paiement"
        verbose_name_plural = "Moyens de paiement"

    name = models.CharField(max_length=255, verbose_name="Nom")
    """
    The name of the PaymentMethod.
    """
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    """
    If False, the PaymentMethod can't be use anywhere.
    """
    is_usable_in_cotisation = models.BooleanField(default=True, verbose_name="Cotisations ?")
    """
    If true, the PaymentMethod can be used to pay cotisation.
    """
    is_usable_in_reload = models.BooleanField(default=True, verbose_name="Rechargements ?")
    """
    If true, the PaymentMethod can be used to reload an user account.
    """
    affect_balance = models.BooleanField(default=False, verbose_name="Affecte le solde")
    """
    If true, the PaymentMethod will decrease the user's balance when used.
    """   
    icon = models.CharField(max_length=255, verbose_name="Icône", blank=True)
    """
    A font awesome icon (without the fa)
    """
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
    """
    If True, the site will be accessible. If False, all the requests are redirect to :func:`~preferences.views.inactive`.
    """
    active_message = models.TextField(blank=True, verbose_name="Message non actif")
    """
    Message displayed on the :func:`~preferences.views.inactive`
    """
    global_message = models.TextField(blank=True, verbose_name="Message global")
    """
    List of messages, separated by a carriage return. One will be chosen randomly at each request on displayed in the header
    """
    president = models.CharField(max_length=255, blank=True, verbose_name="Président")
    """
    The name of the president
    """
    treasurer = models.CharField(max_length=255, blank=True, verbose_name="Trésorier")
    """
    The name of the treasurer
    """
    secretary = models.CharField(max_length=255, blank=True, verbose_name="Secrétaire")
    """
    The name of the secretary
    """
    phoenixTM_responsible = models.CharField(max_length=255, blank=True, verbose_name="Responsable Phœnix Technopôle Metz")
    """
    The name of the people in charge of the club
    """
    use_pinte_monitoring = models.BooleanField(default=False, verbose_name="Suivi de pintes")
    """
    If True, alert will be displayed to allocate pints during order
    """
    lost_pintes_allowed = models.PositiveIntegerField(default=0, verbose_name="Nombre de pintes perdus admises")
    """
    If > 0, a user will be blocked if he has losted more pints than the value
    """
    floating_buttons = models.BooleanField(default=False, verbose_name="Boutons flottants")
    """
    If True, displays floating paymentButtons on the :func:`~gestion.views.manage` view.
    """
    home_text = models.TextField(blank=True, verbose_name="Message d'accueil")
    """
    Text display on the home page
    """
    automatic_logout_time = models.PositiveIntegerField(null=True, verbose_name="Temps de déconnexion automatique")
    """
    Duration after which the user is automatically disconnected if inactive
    """
    statutes = models.FileField(blank=True, null=True, verbose_name="Statuts")
    """
    The file of the statutes
    """
    rules = models.FileField(blank=True, null=True, verbose_name="Règlement intérieur")
    """
    The file of the internal rules
    """
    menu = models.FileField(blank=True, null=True, verbose_name="Menu")
    """
    The file of the menu
    """
    alcohol_charter = models.FileField(blank=True, null=True, verbose_name="Charte alcool")
    """
    The file of the alcohol charter
    """
    history = HistoricalRecords()

class Cotisation(models.Model):
    """
    Stores cotisations.
    """
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name="Montant", validators=[MinValueValidator(0)])
    """
    Price of the cotisation.
    """
    duration = models.PositiveIntegerField(verbose_name="Durée de la cotisation (jours)")
    """
    Duration (in days) of the cotisation
    """
    history = HistoricalRecords()

    def __str__(self):
        return "Cotisation de " + str(self.duration) + " jours pour le prix de " + str(self.amount) + "€"
