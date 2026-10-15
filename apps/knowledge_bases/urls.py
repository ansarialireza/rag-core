from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import KnowledgeBaseViewSet

router = DefaultRouter()
router.register(r'knowledge-bases', KnowledgeBaseViewSet, basename='knowledge-bases')

urlpatterns = [
    path('', include(router.urls)),
]
