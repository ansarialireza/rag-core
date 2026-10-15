from django.urls import path

from .views import RetrievalView

urlpatterns = [
    path('search/', RetrievalView.as_view(), name='retrieval-search'),
]
