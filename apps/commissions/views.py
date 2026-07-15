"""Commission views."""

# Django
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date

# Dajngo REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    CreateAPIView,
    DestroyAPIView,
)
from rest_framework.views import APIView

# Models
from .models import Commission
from users.models import User

# Serializers
from .serializers import CommissionModelSerializer


class CommissionListView(ListAPIView):
    """Vista para listar comisiones activas."""

    queryset = Commission.objects.all()
    serializer_class = CommissionModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get("user", None)

        if user:
            queryset = queryset.filter(users=user)

        return queryset


class CommissionCreateView(CreateAPIView):
    """Vista para crear una comisión."""

    queryset = Commission.objects.all()
    serializer_class = CommissionModelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commission = serializer.save()

        return Response(
            {"message": "Comision creada correctamente", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class CommissionDetailView(RetrieveAPIView):
    """Vista para obtener una comisión por ID."""

    queryset = Commission.objects.all()
    serializer_class = CommissionModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset()


class CommissionUpdateView(UpdateAPIView):
    """Vista para actualizar una comisión."""

    queryset = Commission.objects.all()
    serializer_class = CommissionModelSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CommissionDeleteView(DestroyAPIView):
    """Vista para realizar un Soft Delete en una comisión."""

    queryset = Commission.objects.all()
    serializer_class = CommissionModelSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """Sobrescribe DELETE para hacer un Soft Delete en lugar de eliminar realmente."""
        commission = self.get_object()
        commission.soft_delete()  # Marca como eliminada sin borrarla de la BD
        return Response(
            {"message": "Comisión eliminada correctamente"},
            status=status.HTTP_200_OK,
        )


class CommissionAssignUsersView(APIView):
    """Vista para asignar o remover usuarios de una comisión."""

    permission_classes = [IsAuthenticated]

    def post(self, request, commission_id):
        """Asigna usuarios a una comisión."""
        try:
            commission = Commission.active_objects.get(id=commission_id)
            users_to_add = request.data.get("users", [])

            if not isinstance(users_to_add, list):
                return Response(
                    {"error": "El formato de usuarios debe ser una lista."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            users = User.objects.filter(id__in=users_to_add)
            commission.users.add(*users)

            return Response(
                {"message": "Usuarios asignados correctamente."},
                status=status.HTTP_200_OK,
            )

        except Commission.DoesNotExist:
            return Response(
                {"error": "La comisión no existe o ha sido eliminada."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, commission_id):
        """Remueve usuarios de una comisión."""
        try:
            commission = Commission.active_objects.get(id=commission_id)
            users_to_remove = request.data.get("users", [])

            if not isinstance(users_to_remove, list):
                return Response(
                    {"error": "El formato de usuarios debe ser una lista."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            users = User.objects.filter(id__in=users_to_remove)
            commission.users.remove(*users)

            return Response(
                {"message": "Usuarios removidos correctamente."},
                status=status.HTTP_200_OK,
            )

        except Commission.DoesNotExist:
            return Response(
                {"error": "La comisión no existe o ha sido eliminada."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CommissionActivateView(APIView):
    """Activa una comisión previamente eliminada (Soft Delete)."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, commission_id):
        """Activa una comisión eliminada."""
        print("commission", commission_id)
        try:
            commission = Commission.active_objects.deleted().get(id=commission_id)
            commission.restore()
            return Response(
                {"message": "Comisión activada correctamente."},
                status=status.HTTP_200_OK,
            )
        except Commission.DoesNotExist:
            return Response(
                {"error": "La comisión no existe o ya está activa."},
                status=status.HTTP_404_NOT_FOUND,
            )
