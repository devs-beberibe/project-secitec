from django.db import models
from django.utils import timezone

from called.models import Tecnico


class FichaVerificacaoComponentes(models.Model):
    data_recebimento = models.DateField("data do recebimento", default=timezone.now)
    numero_tombo = models.CharField("Número do tombo", max_length=10, default="")
    deixado = models.CharField("Deixado e conferido por", max_length=50, default="")
    recebido = models.CharField("Recebido por", max_length=50, default="")
    setor = models.CharField("Setor", max_length=50, default="")
    responsavel_pc = models.CharField("Responsável pelo PC", max_length=50, default="")
    descricao_problema = models.CharField("Descrição do Problema", max_length=200, default="")

    observacao = models.TextField("Observações", max_length=300, default="")
    servico_realizado = models.TextField("Serviço Realizado", max_length=300, default="")
    buscado_por = models.CharField("Entrege e conferido por", max_length=50, default="")
    entrege_por = models.CharField("Entrege por", max_length=50, default="")
    laudo = models.CharField("Número do Laudo", max_length=10, default="")
    data_entrega = models.DateField("data da entrega", null=True, default=None)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)

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

    ficha = models.ForeignKey(FichaVerificacaoComponentes, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.IntegerField('Contêm e o estado', choices=CASE)
    observacao_descricao = models.CharField('Observação e descrição', max_length=20, null=True)

    def __str__(self):
        return f'{self.componente}, {self.estado}'