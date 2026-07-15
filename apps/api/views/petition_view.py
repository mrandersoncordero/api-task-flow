"""Petition views."""

# Django
from django.db.models import Q
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
from petitions.models import Petition

# Serializers
from petitions.serializers import (
    PetitionModelserializer,
    PetitionCreateSerializer,
    PetitionFullDetailserializer,
)


# Custom Permissions
from core.permissions import IsAdmin, CanViewPetition
from core.functions import filter_queryset_by_group


class PetitionListView(ListAPIView):
    """Vista para listar peticiones con filtros avanzados."""

    queryset = Petition.active_objects.all()
    serializer_class = PetitionFullDetailserializer
    permission_classes = [IsAuthenticated, CanViewPetition]

    def get_queryset(self):
        """Obtiene el queryset de peticiones aplicando filtros avanzados."""

        user = self.request.user  # Obtener usuario autenticado
        queryset = super().get_queryset()

        queryset = filter_queryset_by_group(super().get_queryset(), user)  # 🔥 Aplicar filtro por grupo

        # 🔥 Diccionario para aplicar filtros dinámicos
        filter_kwargs = {}

        # 📌 Filtros directos
        if self.request.query_params.get("user_email"):
            filter_kwargs["user__email"] = self.request.query_params["user_email"]

        if self.request.query_params.get("department"):
            filter_kwargs["department__id"] = self.request.query_params["department"]

        if self.request.query_params.get("company"):
            filter_kwargs["company__id"] = self.request.query_params["company"]

        if self.request.query_params.get("status_approval"):
            filter_kwargs["status_approval"] = self.request.query_params["status_approval"]

        # 📌 Filtros con búsqueda parcial
        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(Q(title__icontains=title))  # 🔥 Buscar en el título

        # 📌 Filtros de rango de fechas
        date_from = self.request.query_params.get("date_from")
        if date_from:
            parsed_date = parse_date(date_from)
            if parsed_date:
                filter_kwargs["created__gte"] = parsed_date

        date_until = self.request.query_params.get("date_until")
        if date_until:
            parsed_date = parse_date(date_until)
            if parsed_date:
                filter_kwargs["created__lte"] = parsed_date

        # 🔥 Aplicar todos los filtros en una sola operación
        return queryset.filter(**filter_kwargs)


class PetitionDetailView(RetrieveAPIView):

    queryset = Petition.active_objects.all()
    serializer_class = PetitionFullDetailserializer
    permission_classes = [IsAuthenticated, CanViewPetition]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PetitionUpdateView(UpdateAPIView):
    queryset = Petition.active_objects.all()
    serializer_class = PetitionModelserializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PetitionDeleteView(DestroyAPIView):

    queryset = Petition.active_objects.all()
    serializer_class = PetitionModelserializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, *args, **kwargs):
        petition = self.get_object()
        petition.soft_delete()

        return Response(
            {"message": "Petición eliminada correctamente"},
            status=status.HTTP_200_OK,
        )


class PetitionCreateView(CreateAPIView):
    queryset = Petition.active_objects.all()
    serializer_class = PetitionCreateSerializer
    permission_classes = [IsAuthenticated, CanViewPetition]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Guarda la petición

        return Response(
            {"message": "Petición creada correctamente", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class PetitionActivateView(APIView):
    """Activa una petición previamente eliminada (Soft Delete)."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, petition_id):
        """Activa una petición eliminada."""
        try:
            petition = Petition.active_objects.deleted().get(id=petition_id)
            petition.restore()
            return Response(
                {"message": "Petición activada correctamente."},
                status=status.HTTP_200_OK,
            )
        except Petition.DoesNotExist:
            return Response(
                {"error": "La petición no existe o ya está activa."},
                status=status.HTTP_404_NOT_FOUND,
            )
