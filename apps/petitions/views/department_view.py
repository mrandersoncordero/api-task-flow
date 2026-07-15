"""Department views."""

# Django
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date

# Django REST Framework
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
from petitions.models import Company, Department, Petition

# Serializers
from petitions.serializers import DepartmentSerializer, DepartmentCreateSerializer


# Custom Permissions
from core.permissions import IsAdmin, IsManager, IsEmployee, IsClient

class DepartmentListView(ListAPIView):
    queryset = Department.active_objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsManager | IsEmployee | IsClient]

    def get_queryset(self):
        return super().get_queryset()


class DepartmentDetailView(RetrieveAPIView):
    queryset = Department.active_objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepartmentUpdateView(UpdateAPIView):
    queryset = Department.active_objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class DepartmentDeleteView(DestroyAPIView):
    queryset = Department.objects.all()  # 🔥 Permite encontrar eliminados
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, *args, **kwargs):
        department = self.get_object()

        # 🔥 Verificar si hay peticiones activas asociadas a este departamento
        if Petition.active_objects.filter(department=department).exists():
            return Response(
                {
                    "error": "No se puede eliminar el departamento porque tiene peticiones activas."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        department.soft_delete()
        return Response(
            {"message": "Departamento eliminado correctamente"},
            status=status.HTTP_200_OK,
        )


class DepartmentCreateView(CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = serializer.save()

        return Response(
            {"message": "Departamento creado correctamente", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
