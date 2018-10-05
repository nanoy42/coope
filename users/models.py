from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from preferences.models import PaymentMethod, Cotisation

class School(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")

    def __str__(self):
        return self.name

class CotisationHistory(models.Model):
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

class WhiteListHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    paymentDate = models.DateTimeField(auto_now_add=True)
    endDate = models.DateTimeField()
    duration = models.PositiveIntegerField(verbose_name="Durée", help_text="Durée de l'accès gracieux en jour")
    coopeman = models.ForeignKey(User, on_delete=models.PROTECT, related_name="whitelist_made")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=True, null=True)
    cotisationEnd = models.DateTimeField(blank=True, null=True)

    @property
    def balance(self):
        return self.credit - self.debit

    def positiveBalance(self):
        return self.balance >= 0

    @property
    def rank(self):
        return Profile.objects.filter(debit__gte=self.debit).count()

    @property
    def alcohol(self):
        #consos = Consommation.objects.filter(client=self).select_related('produit')
        #alcool = 0
        #for conso in consos:
            #produit = conso.produit
            #alcool += conso.nombre * float(produit.deg) * produit.volume * 0.79 /10 /1000
        return 0

    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()