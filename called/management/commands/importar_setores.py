from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook

from called.models import Secretary, Sector


class Command(BaseCommand):
    help = "Importa secretarias e setores do Excel"

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=str)

    def handle(self, *args, **options):
        try:
            workbook = load_workbook(
                options["arquivo"],
                read_only=True,
                data_only=True,
            )
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc))

        try:
            if "Todos os pontos" not in workbook.sheetnames:
                raise CommandError(
                    "A aba 'Todos os pontos' não foi encontrada."
                )

            sheet = workbook["Todos os pontos"]

            secretarias_criadas = 0
            setores_criados = 0
            setores_existentes = 0

            with transaction.atomic():
                for linha in sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                ):
                    nome_secretaria, nome_setor = linha[:2]

                    if not nome_secretaria or not nome_setor:
                        continue

                    nome_secretaria = str(
                        nome_secretaria
                    ).strip()

                    nome_setor = str(nome_setor).strip()

                    secretaria, criada = (
                        Secretary.objects.get_or_create(
                            secretary_name__iexact=nome_secretaria,
                            defaults={
                                "secretary_name": nome_secretaria
                            },
                        )
                    )

                    if criada:
                        secretarias_criadas += 1

                    _, criado = Sector.objects.get_or_create(
                        secretary=secretaria,
                        sector_name__iexact=nome_setor,
                        defaults={
                            "sector_name": nome_setor
                        },
                    )

                    if criado:
                        setores_criados += 1
                    else:
                        setores_existentes += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Secretarias criadas: {secretarias_criadas}\n"
                    f"Setores criados: {setores_criados}\n"
                    f"Setores existentes: {setores_existentes}"
                )
            )
        finally:
            workbook.close()