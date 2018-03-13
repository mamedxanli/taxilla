from django.db import models

class BaseModel(models.Model):
    """
    This abstract base model adds below two fields to all models who inherit
    this class.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
