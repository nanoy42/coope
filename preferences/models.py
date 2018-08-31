from django.db import models

class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GeneralPreferences(models.Model):
    is_active = models.BooleanField(default=True)
    active_message = models.TextField(blank=True)
    global_message = models.TextField(blank=True)
    president = models.CharField(max_length=255, blank=True)
    vice_president = models.CharField(max_length=255, blank=True)
    treasurer = models.CharField(max_length=255, blank=True)
    secretary = models.CharField(max_length=255, blank=True)
    brewer = models.CharField(max_length=255, blank=True)
    grocer = models.CharField(max_length=255, blank=True)
