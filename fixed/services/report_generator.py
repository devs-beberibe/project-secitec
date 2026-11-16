"""Geração do laudo técnico a partir da ficha de manutenção.

Mantém o fluxo do script-laudo original: abre o modelo DOCX, substitui os
placeholders, cria as listas de serviços/componentes e salva um novo DOCX.
"""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone


REPORT_TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "report_templates"
    / "Laudo 00 - Modelo.docx"
)

MONTHS = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)


def _person_name(person):
    user = getattr(person, "user", None)
    if user:
        return user.get_full_name().strip() or user.get_username()
    return str(person or "Não informado")


def _lines(value):
    return [line.strip(" -•\t") for line in (value or "").splitlines() if line.strip()]


def _report_data(sheet):
    sector = sheet.secretary_sector
    components = []
    for item in sheet.components_status.select_related("component").all():
        description = f" — {item.description_report}" if item.description_report else ""
        components.append(
            f"{item.component.name}: {item.get_status_display()}{description}"
        )

    services = _lines(sheet.realized_service)
    if sheet.observation:
        services.append(f"Observações: {sheet.observation}")

    return {
        "numero_laudo": str(sheet.pk),
        "nome_tecnico": _person_name(sheet.technician),
        "problema_equipamento": sheet.problem_description,
        "secretaria": sector.secretary.secretary_name,
        "setor": sector.sector_name,
        "numero_tombamento": sheet.serial_number or "Não informado",
        "componentes": components or ["Conferência de componentes não informada."],
        "servicos_realizados": services or ["Serviço realizado não informado."],
    }


def _replace_list(paragraph, placeholder, values):
    if placeholder not in paragraph.text:
        return False
    for value in values:
        new_paragraph = paragraph.insert_paragraph_before()
        new_paragraph.style = paragraph.style
        new_paragraph.add_run(f"✓ {value}")
        _compact_paragraph(new_paragraph, font_size=11, after=0)
    paragraph._element.getparent().remove(paragraph._element)
    return True


def _compact_paragraph(paragraph, font_size=10, before=0, after=2):
    from docx.shared import Pt

    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1
    for run in paragraph.runs:
        run.font.size = Pt(font_size)


def build_report_document(sheet, template_path=REPORT_TEMPLATE):
    """Monta o DOCX em memória e não altera o banco nem o storage."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "Dependência inválida. Remova o pacote 'docx' e instale "
            "'python-docx'."
        ) from error

    data = _report_data(sheet)
    report_date = timezone.localdate()
    formatted_date = (
        f"{report_date.day} de {MONTHS[report_date.month - 1]} "
        f"de {report_date.year}"
    )
    left = f"Laudo {data['numero_laudo']}/{report_date.year}"
    right = f"Beberibe, {formatted_date}."
    heading = f"{right}\n{left}"

    document = Document(str(template_path))
    replacements = {
        "{{problema_equipamento}}": data["problema_equipamento"],
        "{{nome_tecnico}}": f"{data['nome_tecnico']}\n",
        "{{numero_laudo}}": data["numero_laudo"],
        "{{cabeca}}": heading,
        "{{secretaria_setor}}": (
            f"Secretaria / Setor: {data['secretaria']} – {data['setor']}"
        ),
        "{{numero_tombamento}}": f"Tombamento: {data['numero_tombamento']}",
    }

    # list() é necessário porque os placeholders de listas são removidos.
    for paragraph in list(document.paragraphs):
        if _replace_list(
            paragraph,
            "{{servicos_realizados}}",
            data["servicos_realizados"],
        ):
            continue
        if _replace_list(paragraph, "{{componentes}}", data["componentes"]):
            continue
        if "{{marca_modelo}}" in paragraph.text:
            # O modelo MaintenanceSheet atual não possui marca/modelo.
            paragraph._element.getparent().remove(paragraph._element)
            continue
        if "Os demais componentes estão funcionando normalmente." in paragraph.text:
            paragraph.text = paragraph.text.replace(
                "Os demais componentes estão funcionando normalmente.",
                "Conferência dos componentes:",
            )
            _compact_paragraph(paragraph, font_size=11, before=11, after=2)
        if paragraph.text == "Conferência dos componentes:":
            _compact_paragraph(paragraph, font_size=11, before=11, after=2)
        if paragraph.text.startswith(
            "Informo que após análise técnica realizada"
        ):
            _compact_paragraph(paragraph, font_size=11, before=11, after=3)
        if paragraph.text in (
            "Descrição após manutenção do equipamento:",
            "Descrição do computador analisado:",
        ):
            _compact_paragraph(paragraph, font_size=11, before=11, after=2)
        for placeholder, value in replacements.items():
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, value)
                if placeholder == "{{cabeca}}":
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    _compact_paragraph(paragraph, font_size=12, after=6)
                elif placeholder == "{{problema_equipamento}}":
                    _compact_paragraph(paragraph, font_size=11, after=0)
                elif placeholder in (
                    "{{secretaria_setor}}",
                    "{{numero_tombamento}}",
                ):
                    _compact_paragraph(paragraph, font_size=11, after=0)

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def generate_technical_report(sheet):
    """Gera e vincula o laudo à ficha depois da manutenção."""
    content = build_report_document(sheet)
    year = timezone.localdate().year
    filename = f"Laudo_{sheet.pk}_{year}.docx"
    sheet.technical_report.save(filename, ContentFile(content), save=False)
    sheet.report_generated_at = timezone.now()
    sheet.save(update_fields=("technical_report", "report_generated_at"))
    return sheet.technical_report
