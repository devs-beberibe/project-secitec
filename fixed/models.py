from django.db import models
from django.utils import timezone

from django.conf import settings



class MaintenanceSheet(models.Model):
    # Atributos referentes ao recebimento

    receipt_date = models.DateField("Data do recebimento", default=timezone.now)
    serial_number = models.CharField("Número do tombo/série", max_length=30, null=True, blank=True )
    #Quem recebeu o computador
    receipt = models.ForeignKey("core.User_sec", on_delete=models.CASCADE, related_name="Recebido por")
    #Quem conferiu/Tecnico
    technician = models.ForeignKey(
        "core.Tecs", on_delete=models.CASCADE, related_name="tecnico_responsavel"
    )
    secretary_sector = models.ForeignKey(
        "called.Sector", on_delete=models.CASCADE, related_name="secretaria_setor"
    )
    #Responsavel que utiliza o pc recebiddo
    pc_responsible = models.CharField("responsavel_pc", max_length=50, default="")
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
    #A quem entregou
    search_by = models.CharField(
        "Entrege e conferido por", max_length=50, default="", null=True, blank=True
    )
    #Quem entregou
    delivered_by = models.ForeignKey(
        "core.User_sec",on_delete=models.CASCADE,related_name="entregue_por",null=True,blank=True,
    )
    report = models.CharField(
        "Número do Laudo", max_length=10, default="", null=True, blank=True
    )
    delivery_date = models.DateField(
        "data da entrega", null=True, blank=True, default=None
    )
    def __str__(self):
        return self.serial_number


class Components(models.Model):
    name = models.CharField("Nome", max_length=50, unique=True)

    def __str__(self):
        return self.name


class ComponentStatus(models.Model):
    CASE = (
        (1, "Contêm e bom estado"),
        (2, "Contêm e mau estado"),
        (3, "Não contêm"),
    )

    sheet = models.ForeignKey(
        MaintenanceSheet, on_delete=models.CASCADE, related_name="components_status"
    )
    component = models.ForeignKey(Components, on_delete=models.CASCADE)
    status = models.IntegerField("Contêm e o estado", choices=CASE)
    description_report = models.CharField(
        "Observação e descrição", max_length=20, null=True
    )

    def __str__(self):
        return f"{self.component}, {self.status}"
