"""Department views."""

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

# Models
from petitions.models import Company, Petition
from users.models import HumanResource

# Serializers
from petitions.serializers import CompanySerializer, CompanyCreateSerializer


# Custom Permissions
from core.permissions import IsAdmin, IsManager, IsEmployee, IsClient


class CompanyListView(ListAPIView):
    queryset = Company.active_objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsManager | IsEmployee | IsClient]

    def get_queryset(self):
        return super().get_queryset()


class CompanyDetailView(RetrieveAPIView):
    queryset = Company.active_objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CompanyUpdateView(UpdateAPIView):
    queryset = Company.active_objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CompanyDeleteView(DestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, *args, **kwargs):
        company = self.get_object()
        # 🔥 Verificar si hay peticiones activas asociadas a esta empresa
        if Petition.active_objects.filter(company=company).exists():
            return Response(
                {
                    "error": "No se puede eliminar la empresa porque tiene peticiones activas."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # 🔥 Verificar si hay recursos humanos activos asociados a esta empresa
        if HumanResource.active_objects.filter(company=company).exists():
            return Response(
                {
                    "error": "No se puede eliminar la empresa porque tiene usuarios activos."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        company.soft_delete()
        return Response(
            {"message": "Empresa eliminada correctamente"},
            status=status.HTTP_200_OK,
        )


class CompanyCreateView(CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Empresa creada correctamente", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )