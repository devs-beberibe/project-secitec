from rest_framework import viewsets, mixins, status
from .models import *
from core.models import Tecs
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.response import Response

    
    
class TecsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tecs.objects.all()
    serializer_class = TechnicianSerializer
    permisison_classes = [AllowAny]


class CallViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):

        if self.action == "abrir":
            return OpenCallSerializer

        if self.action == "fechar_chamado":
            return FinishCallSerializer

        return CallSerializer

    def get_queryset(self):

        queryset = Call.objects.all()
        if self.action == "list":
            return queryset.filter(
                status__in=["IMP", "OPN"],
                date_end__isnull=True,
            ).order_by(
                "priority",
                "date_start",
                "id",
            )

        return queryset

    @action(
        detail=False,
        methods=["post"],
        url_path="abrir",
    )
    def abrir(self, request):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        sector = serializer.validated_data[
            "sector"
        ]

        priority = serializer.validated_data.get(
            "priority",
            1,
        )

        if sector.secretary_id in [1, 2]:
            priority = 0

        chamado = serializer.save(
            status="OPN",
            priority=priority,
            date_start=timezone.localdate(),
        )

        return Response(
            CallSerializer(chamado).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="realizar",
    )
    def realizar(self, request, pk=None):

        chamado = self.get_object()

        if chamado.status == "CLS":
            return Response(
                {
                    "detail": (
                        "Não é possível realizar "
                        "um chamado já encerrado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if chamado.status == "IMP":
            return Response(
                {
                    "detail": (
                        "Este chamado já está "
                        "em andamento."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        chamado.status = "IMP"

        chamado.save(
            update_fields=["status"]
        )

        return Response(
            CallSerializer(chamado).data,
            status=status.HTTP_200_OK,
        )



    @action(
        detail=True,
        methods=["post"],
        url_path="fechar-chamado",
    )
    def fechar_chamado(
        self,
        request,
        pk=None,
    ):

        chamado = self.get_object()

        if chamado.status == "CLS":
            return Response(
                {
                    "detail": (
                        "Este chamado já foi encerrado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if chamado.status != "IMP":
            return Response(
                {
                    "detail": (
                        "O chamado precisa estar "
                        "em andamento antes de ser "
                        "encerrado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            chamado,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        chamado = serializer.save(
            status="CLS",
            date_end=timezone.localdate(),
        )

        return Response(
            CallSerializer(chamado).data,
            status=status.HTTP_200_OK,
        )