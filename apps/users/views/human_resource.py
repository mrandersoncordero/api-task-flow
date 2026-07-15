from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView

from users.models.human_resources_model import HumanResource
from users.serializers.human_resourse import (
    HumanResourceModelSerializer,
    HumanResourceCreateSerializer,
)


# Custom Permissions
from core.permissions import IsAdmin, IsManager, IsClient, IsEmployee

class HumanResourceCreateAPIView(CreateAPIView):
    """API para crear un perfil de HumanResource."""

    serializer_class = HumanResourceCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # Solo usuarios autenticados pueden crear HR

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class HumanResourceDetailUpdateAPIView(RetrieveUpdateAPIView):
    """API para obtener o actualizar el perfil de HumanResource del usuario autenticado."""

    serializer_class = HumanResourceModelSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        """Retorna el perfil de HumanResource del usuario autenticado."""
        return self.request.user.humanresource

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)