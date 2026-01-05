import uuid
from django.db import models
from apps.core.models import BaseModel

class SkillCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')

    class Meta:
        db_table = 'skill_categories'
        verbose_name_plural = 'Skill categories'

    def __str__(self):
        return self.name