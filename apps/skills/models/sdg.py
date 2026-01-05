import uuid
from django.db import models
from apps.core.models import BaseModel

class SustainableDevelopmentGoal(BaseModel):
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'sustainable_development_goals'
        ordering = ['number']

    def __str__(self):
        return f"SDG {self.number}: {self.title}"