from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from preferences.models import PaymentMethod

class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Cotisation(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    paymentDate = models.DateTimeField(auto_now_add=True)
    endDate = models.DateTimeField()
    paymentMethod = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)

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
        return self.solde() >= 0

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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
