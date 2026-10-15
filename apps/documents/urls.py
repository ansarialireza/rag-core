from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentUploadView, DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')

urlpatterns = [
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('', include(router.urls)),
]
