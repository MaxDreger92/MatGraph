from django.db import models


class ImportingReport(models.Model):

    class Meta:
        verbose_name = 'Importing Report'
        verbose_name_plural = 'Importing Reports'

    type = models.CharField(max_length=60)
    date = models.DateTimeField(auto_now_add=True)
    report = models.TextField()

    def __str__(self):
        return f'Importing Report ({self.type}, {self.date})'