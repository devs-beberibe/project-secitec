from django.db import models
from django.utils import timezone

from django.conf import settings

from called.models import *





class MaintenanceSheet(models.Model):
    # Atributos referentes ao recebimento
    
    receipt_date = models.DateField("data do recebimento", default=timezone.now)
    serial_number = models.CharField("Número do tombo/série", max_length=30, default="")
    left_by = models.CharField("Deixado e conferido por", max_length=50, default="")
    receipt = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="recebido_por"
    )
    secretary_sector = models.ForeignKey(
        "called.SecretarySector",
        on_delete=models.CASCADE
    )
    pc_responsible = models.CharField("Responsável pelo PC", max_length=50, default="")
    problem_description = models.CharField(
        "Descrição do Problema", max_length=200, default=""
    )
    contact = models.CharField("Contato", max_length=50)

    # Atributos referentes a entrega
    observation = models.TextField(
        "Observações", max_length=300, default="", null=True, blank=True
    )
    realized_service = models.TextField(
        "Serviço Realizado", max_length=300, default="", null=True, blank=True
    )
    search_by = models.CharField(
        "Entrege e conferido por", max_length=50, default="", null=True, blank=True
    )
    delivered_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="entregue_por",
    null=True,
    blank=True,
)
    report = models.CharField(
        "Número do Laudo", max_length=10, default="", null=True, blank=True
    )
    delivery_date = models.DateField(
        "data da entrega", null=True, blank=True, default=None
    )
    technician = models.ForeignKey(
        Technician, on_delete=models.CASCADE, null=True, blank=True
    )


    def __str__(self):
        return self.serial_number


class Component(models.Model):
    name = models.CharField("Nome", max_length=20, unique=True)

    def __str__(self):
        return self.name


class ComponentStatus(models.Model):
    CASE = (
        (1, "Contêm e bom estado"),
        (2, "Contêm e mau estado"),
        (3, "Não contêm"),
    )

    sheet = models.ForeignKey(MaintenanceSheet, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    status = models.IntegerField("Contêm e o estado", choices=CASE)
    description_report = models.CharField(
        "Observação e descrição", max_length=20, null=True
    )

    def __str__(self):
        return f"{self.component}, {self.status}"
