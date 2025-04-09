from django.db import models
from accounts.models import CustomUser
from accounts.base_model import BaseModel

# Create your models here.


class Industry(BaseModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name_plural = "Industries"
        verbose_name = "Industry"

    def __str__(self):
        return self.name


class IndustryUser(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="industryuser",
    )
    industry = models.ForeignKey(
        Industry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="industryuser_industry",
    )
    price = models.FloatField(null=True, blank=True)
    internship = models.CharField(max_length=255, null=True, blank=True)
    star = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Industry Users"
        verbose_name = "Industry User"

    def __str__(self):
        return f"{self.user.username if self.user else ''} - {self.industry.name if self.industry else ''}- {self.star}"
