from django.db import models


class Snippet(models.Model):
    slug = models.CharField(max_length=50)
    html = models.TextField()

    def __str__(self):
        return self.slug