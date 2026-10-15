from django.db import models


class RetrievalQuery(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    query_text = models.TextField()
