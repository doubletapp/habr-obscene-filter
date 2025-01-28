from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ObsceneWord(models.Model):
    value = models.CharField(max_length=255, unique=True, verbose_name="Word value")
    normalized_value = models.CharField(max_length=1023, verbose_name="Normalized word value")
    similarity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], null=True, blank=True)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "Obscene word"
        verbose_name_plural = "Obscene words"
        indexes = [GinIndex(name="obscene_word_value", fields=["normalized_value"], opclasses=["gin_trgm_ops"])]


class SuspiciousWord(models.Model):
    class SuspiciousWordStatuses(models.IntegerChoices):
        PENDING = 0, "Pending"
        ADDED = 1, "Added to dictionary"
        DECLINED = 2, "Declined"

    value = models.CharField(max_length=255, unique=True, verbose_name="Word value")
    status = models.IntegerField(
        choices=SuspiciousWordStatuses.choices, default=SuspiciousWordStatuses.PENDING, verbose_name="Status"
    )

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "Suspicious word"
        verbose_name_plural = "Suspicious words"
