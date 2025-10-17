from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

from called.models import Tecnico


class Setor(models.Model):

    nome = models.CharField("Nome do Setor", max_length=50, unique=True)

    def __str__(self):
        return self.nome


class FichaDeManutencao(models.Model):
    # Atributos referentes ao recebimento
    data_recebimento = models.DateField("data do recebimento", default=timezone.now)
    numero_tombo = models.CharField("Número do tombo/série", max_length=30, default="")
    deixado = models.CharField("Deixado e conferido por", max_length=50, default="")
    recebido = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recebido_por")
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    responsavel_pc = models.CharField("Responsável pelo PC", max_length=50, default="")
    descricao_problema = models.CharField("Descrição do Problema", max_length=200, default="")
    contato = models.CharField("Contato", max_length=50)

    # Atributos referentes a entrega
    observacao = models.TextField("Observações", max_length=300, default="", null=True, blank=True)
    servico_realizado = models.TextField("Serviço Realizado", max_length=300, default="", null=True, blank=True)
    buscado_por = models.CharField("Entrege e conferido por", max_length=50, default="", null=True, blank=True)
    entrege_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entrege_por", null=True, blank=True)
    laudo = models.CharField("Número do Laudo", max_length=10, default="", null=True, blank=True)
    data_entrega = models.DateField("data da entrega", null=True, blank=True, default=None)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.numero_tombo


class Componente(models.Model):
    nome = models.CharField("Nome", max_length=20, unique=True)

    def __str__(self):
        return self.nome


class ComponenteEstado(models.Model):
    CASE = (
        (1, "Contêm e bom estado"),
        (2, "Contêm e mau estado"),
        (3, "Não contêm"),
    )

    ficha = models.ForeignKey(FichaDeManutencao, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.IntegerField('Contêm e o estado', choices=CASE)
    observacao_descricao = models.CharField('Observação e descrição', max_length=20, null=True)

    def __str__(self):
        return f'{self.componente}, {self.estado}'

    