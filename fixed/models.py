from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class MaintenanceSheet(models.Model):
    RECEIVED = "RCV"
    IN_MAINTENANCE = "MNT"
    DELIVERED = "DLV"
    STATUS_CHOICES = (
        (RECEIVED, "Recebido"),
        (IN_MAINTENANCE, "Manutencão Feita"),
        (DELIVERED, "Entregue"),
    )

    status = models.CharField(
        "Situação",
        max_length=3,
        choices=STATUS_CHOICES,
        default=RECEIVED,
        db_index=True,
    )
    receipt_date = models.DateField(
        "Data do recebimento",
        default=timezone.localdate,
    )
    serial_number = models.CharField(
        "Número do tombo/série",
        max_length=30,
        blank=True,
        default="",
    )
    receipt = models.ForeignKey(
        "core.User_sec",
        on_delete=models.PROTECT,
        related_name="fichas_recebidas",
        verbose_name="Recebido por",
    )
    technician = models.ForeignKey(
        "core.Tecs",
        on_delete=models.PROTECT,
        related_name="fichas_responsaveis",
        verbose_name="Técnico responsável",
        null=True,
        blank=True,
    )
    secretary_sector = models.ForeignKey(
        "called.Sector",
        on_delete=models.PROTECT,
        related_name="fichas_manutencao",
        verbose_name="Secretaria/setor",
    )
    pc_responsible = models.CharField(
        "Responsável pelo equipamento",
        max_length=50,
    )
    problem_description = models.CharField(
        "Descrição do problema",
        max_length=200,
    )
    contact = models.CharField("Contato", max_length=50)
    observation = models.TextField(
        "Observações",
        max_length=300,
        blank=True,
        default="",
    )
    realized_service = models.TextField(
        "Serviço realizado",
        max_length=300,
        blank=True,
        default="",
    )
    search_by = models.CharField(
        "Entregue e conferido por",
        max_length=50,
        blank=True,
        default="",
    )
    delivered_by = models.ForeignKey(
        "core.User_sec",
        on_delete=models.PROTECT,
        related_name="fichas_entregues",
        null=True,
        blank=True,
    )
    delivery_date = models.DateField(
        "Data da entrega",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-receipt_date", "-id")

    @property
    def situation(self):
        return {
            self.RECEIVED: "RECEIVED",
            self.IN_MAINTENANCE: "IN_MAINTENANCE",
            self.DELIVERED: "DELIVERED",
        }[self.status]

    def __str__(self):
        return f"Ficha #{self.pk} - {self.serial_number or 'sem tombo/série'}"


class Components(models.Model):
    name = models.CharField("Nome", max_length=50, unique=True)
    display_order = models.PositiveSmallIntegerField(
        "Ordem de exibição",
        default=0,
        validators=[MinValueValidator(0)],
    )
    active = models.BooleanField("Ativo", default=True)

    class Meta:
        ordering = ("display_order", "id")
        verbose_name = "Componente"
        verbose_name_plural = "Componentes"

    def __str__(self):
        return self.name


class ComponentStatus(models.Model):
    GOOD = 1
    BAD = 2
    ABSENT = 3
    CASE = (
        (GOOD, "Contém e está em bom estado"),
        (BAD, "Contém e está em mau estado"),
        (ABSENT, "Não contém"),
    )

    sheet = models.ForeignKey(
        MaintenanceSheet,
        on_delete=models.CASCADE,
        related_name="components_status",
    )
    component = models.ForeignKey(
        Components,
        on_delete=models.PROTECT,
        related_name="status_records",
    )
    status = models.PositiveSmallIntegerField(
        "Presença e estado",
        choices=CASE,
    )
    description_report = models.CharField(
        "Observação e descrição",
        max_length=200,
        blank=True,
        default="",
    )

    class Meta:
        ordering = ("component__display_order", "component_id")
        constraints = [
            models.UniqueConstraint(
                fields=("sheet", "component"),
                name="unique_component_per_maintenance_sheet",
            )
        ]

    def __str__(self):
        return f"{self.component}: {self.get_status_display()}"
