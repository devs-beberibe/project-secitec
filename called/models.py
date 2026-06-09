from django.db import models
from django.utils import timezone

from django.conf import settings


# Create your models here.
class SecretarySector(models.Model):

    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
 

class Call(models.Model):

    STATUS_CALLED = [
        ("OPN", "abertos"),
        ("IMP", "emAndamento"),
        ("CLS", "encerrados"),
    ]

    secretary_sector = models.ForeignKey(SecretarySector, on_delete=models.CASCADE)
    problem = models.TextField("Problema", max_length=250)
    requester = models.CharField("Requisitante", max_length=100)
    status = models.CharField(
        "Status do Chamado", max_length=3, choices=STATUS_CALLED, default="OPN"
    )
    date_start = models.DateField(default=timezone.now)
    date_end = models.DateField(default=None, blank=True, null=True)
    solution = models.TextField("Solução", max_length=250, null=True, blank=True)



    def __str__(self):
        return SecretarySector.objects.get(pk=self.secretary_sector.id).name


class Technician(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"