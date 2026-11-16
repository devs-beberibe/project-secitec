from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Components, MaintenanceSheet
from .permissions import (
    IsAdministrativeOrTechnician,
    IsTechnician,
)
from .serializers import (
    ComponentSerializer,
    DeliverySerializer,
    MaintenanceSerializer,
    MaintenanceSheetSerializer,
    PublicTrackingSerializer,
    ReceiptSerializer,
)
from .services.report_generator import generate_technical_report


REPORT_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


class ReportGenerationError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Não foi possível gerar o laudo técnico."


class MaintenanceSheetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MaintenanceSheetSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = (
        "=id",
        "serial_number",
        "pc_responsible",
        "problem_description",
        "secretary_sector__sector_name",
        "secretary_sector__secretary__secretary_name",
    )
    ordering_fields = ("id", "receipt_date", "delivery_date")
    ordering = ("-receipt_date", "-id")
    queryset = (
        MaintenanceSheet.objects
        .select_related(
            "receipt",
            "technician__user",
            "secretary_sector__secretary",
            "delivered_by",
        )
        .prefetch_related("components_status__component")
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            requested_status = self.request.query_params.get("status")
            valid_statuses = {choice[0] for choice in MaintenanceSheet.STATUS_CHOICES}
            if requested_status in valid_statuses:
                queryset = queryset.filter(status=requested_status)
        return queryset

    def get_permissions(self):
        if self.action in (
            "public_tracking",
            "public_search",
            "public_report",
            "components",
        ):
            return [AllowAny()]
        if self.action == "report":
            return [IsAuthenticated()]
        if self.action == "generate_report":
            return [IsAuthenticated(), IsAdministrativeOrTechnician()]
        if self.action == "recebimento":
            return [IsAuthenticated(), IsAdministrativeOrTechnician()]
        if self.action == "manutencao":
            return [IsAuthenticated(), IsTechnician()]
        if self.action == "entrega":
            return [IsAuthenticated(), IsAdministrativeOrTechnician()]
        return [IsAuthenticated(), IsAdministrativeOrTechnician()]

    def get_serializer_class(self):
        if self.action == "recebimento":
            return ReceiptSerializer
        if self.action == "manutencao":
            return MaintenanceSerializer
        if self.action == "entrega":
            return DeliverySerializer
        if self.action in ("public_tracking", "public_search"):
            return PublicTrackingSerializer
        if self.action == "components":
            return ComponentSerializer
        return MaintenanceSheetSerializer

    @action(detail=False, methods=("post",), url_path="recebimento")
    def recebimento(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sheet = serializer.save()
        sheet = self.get_queryset().get(pk=sheet.pk)
        return Response(
            MaintenanceSheetSerializer(sheet).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=("post",), url_path="manutencao")
    @transaction.atomic
    def manutencao(self, request, pk=None):
        sheet = (
            MaintenanceSheet.objects
            .select_for_update()
            .get(pk=self.get_object().pk)
        )
        serializer = self.get_serializer(sheet, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sheet = self.get_queryset().get(pk=sheet.pk)
        return Response(MaintenanceSheetSerializer(sheet).data)

    @action(detail=True, methods=("post",), url_path="entrega")
    @transaction.atomic
    def entrega(self, request, pk=None):
        # Lock prevents two users from delivering the same sheet concurrently.
        sheet = (
            MaintenanceSheet.objects
            .select_for_update()
            .get(pk=self.get_object().pk)
        )
        serializer = self.get_serializer(
            sheet,
            data=request.data,
            partial=False,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sheet = self.get_queryset().get(pk=sheet.pk)
        return Response(MaintenanceSheetSerializer(sheet).data)

    @action(
        detail=False,
        methods=("get",),
        url_path=r"consulta/(?P<sheet_number>[0-9]+)",
    )
    def public_tracking(self, request, sheet_number=None):
        try:
            sheet = self.get_queryset().get(pk=sheet_number)
        except MaintenanceSheet.DoesNotExist as error:
            raise NotFound("Ficha não encontrada.") from error
        return Response(self.get_serializer(sheet).data)

    @action(detail=False, methods=("get",), url_path="consulta")
    def public_search(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            raise ValidationError({"q": "Informe o que deseja buscar."})

        filters = (
            Q(serial_number__icontains=query)
            | Q(secretary_sector__sector_name__icontains=query)
        )
        if query.isdigit():
            filters |= Q(pk=int(query))

        sheets = self.get_queryset().filter(filters).distinct()[:50]
        if not sheets:
            raise NotFound("Ficha não encontrada.")
        return Response(self.get_serializer(sheets, many=True).data)

    @action(detail=False, methods=("get",), url_path="componentes")
    def components(self, request):
        queryset = Components.objects.filter(active=True)
        return Response(self.get_serializer(queryset, many=True).data)

    def _report_response(self, sheet):
        if not sheet.technical_report:
            raise NotFound("O laudo desta ficha ainda não foi gerado.")
        try:
            report_file = sheet.technical_report.open("rb")
        except (FileNotFoundError, OSError) as error:
            raise NotFound("O arquivo do laudo não foi encontrado.") from error
        filename = f"Laudo {sheet.pk}.docx"
        return FileResponse(
            report_file,
            as_attachment=False,
            filename=filename,
            content_type=REPORT_CONTENT_TYPE,
        )

    @action(
        detail=True,
        methods=("get",),
        url_path="laudo",
        url_name="laudo",
    )
    def report(self, request, pk=None):
        return self._report_response(self.get_object())

    @action(
        detail=True,
        methods=("get",),
        url_path="laudo-publico",
        url_name="laudo-publico",
    )
    def public_report(self, request, pk=None):
        return self._report_response(self.get_object())

    @action(
        detail=True,
        methods=("post",),
        url_path="gerar-laudo",
        url_name="gerar-laudo",
    )
    @transaction.atomic
    def generate_report(self, request, pk=None):
        sheet = (
            MaintenanceSheet.objects
            .select_for_update()
            .get(pk=self.get_object().pk)
        )
        if sheet.status == MaintenanceSheet.RECEIVED:
            raise ValidationError(
                {"detail": "Realize a manutenção antes de gerar o laudo."}
            )
        try:
            generate_technical_report(sheet)
        except Exception as error:
            raise ReportGenerationError() from error
        sheet = self.get_queryset().get(pk=sheet.pk)
        return Response(
            MaintenanceSheetSerializer(
                sheet,
                context=self.get_serializer_context(),
            ).data
        )
