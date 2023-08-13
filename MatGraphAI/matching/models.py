from django.db import models


class MatchingReport(models.Model):

    class Meta:
        verbose_name = 'Matching Report'
        verbose_name_plural = 'Matching Reports'

    type = models.CharField(max_length=60)
    date = models.DateTimeField(auto_now_add=True)
    report = models.TextField()

    def __str__(self):
        return f'Matching Report ({self.type}, {self.date})'