from django.db import models
from django.utils import timezone

from django.conf import settings

from django.contrib.auth.models import User, Group

from core.models import Tecs

# Create your models here.

class Secretary(models.Model):
    
    secretary_name = models.CharField(
        max_length=255,
        verbose_name="Secretaria",
    )

    def __str__(self):
        return self.secretary_name


class Sector(models.Model):
    
    sector_name = models.CharField(
        max_length=255,
        verbose_name="Setor"
    )

    secretary = models.ForeignKey(
        Secretary,
        on_delete=models.CASCADE,
        related_name="setores",
        verbose_name="Seceretaria do setor"
    )
    
    def __str__(self):
        return f"{self.sector_name} - {self.secretary}"

class Call(models.Model):

    STATUS_CALLED = [
        ("OPN", "Aberto"),
        ("IMP", "Em andamento"),
        ("CLS", "Encerrado"),
    ]
    
    PRIORITY = [
        (0, "Prioridade Alta"),
        (1, "Prioridade Média"),
        (2, "Prioridade Baixa"),
    ]

    sector = models.ForeignKey(
        Sector, 
        on_delete=models.CASCADE,
        verbose_name="Setor"
    )
    problem = models.TextField("Problema", max_length=250)
    requester = models.CharField("Requisitante", max_length=250)
    status = models.CharField(
        "Status do Chamado",max_length=3, choices=STATUS_CALLED, default="OPN",
    )
    priority = models.IntegerField(
        "Prioridade do chamado",choices=PRIORITY, default=1
    )
    date_start = models.DateField(default=timezone.now)
    tecs = models.ManyToManyField(
        "core.Tecs",
        related_name="chamados",
        blank=True,
    )
    date_end = models.DateField(default=None, blank=True, null=True)
    solution = models.TextField("Solução", max_length=250, null=True, blank=True)

    def __str__(self):
        return f"Chamado {self.pk} - {self.sector}"
