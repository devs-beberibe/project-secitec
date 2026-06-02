from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


# Create your models here.
class Secretary(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Call(models.Model):

    STATUS_CALLED = [
        ("OPN", "abertos"),
        ("IMP", "emAndamento"),
        ("CLS", "encerrados"),
    ]

    secretary_sector = models.ForeignKey(Secretary, on_delete=models.CASCADE)
    problem = models.TextField("Problema", max_length=250)
    requester = models.CharField("Requisitante", max_length=100)
    status = models.CharField(
        "Status do Chamado", max_length=3, choices=STATUS_CALLED, default="OPN"
    )
    date_start = models.DateField(default=timezone.now)
    date_end = models.DateField(default=None, blank=True, null=True)
    solution = models.TextField("Solução", max_length=250, null=True, blank=True)

    def __str__(self):
        return Secretary.objects.get(pk=self.secretary_sector.id).name


class Technician(models.Model):

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="technician",
    )

    called = models.ManyToManyField(Call)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"
