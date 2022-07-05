from datetime import datetime
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30)
    sequence = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-list', kwargs={'category': self.slug})

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["sequence", "name"]


class Developer(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    url = models.URLField()
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Feature(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(null=True, blank=True)
    sequence = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sequence", "name"]


class Software(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    developer = models.ForeignKey(Developer, blank=True, null=True, on_delete=models.SET_NULL)
    url = models.URLField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    features = models.ManyToManyField(Feature, null=True, blank=True)
    free = models.BooleanField(default=False, blank=True, null=False)
    mac = models.BooleanField(default=True, blank = True, null=False)
    windows = models.BooleanField(default=True, blank=True, null=False)
    linux = models.BooleanField(default=False, blank=True, null=False)
    active = models.BooleanField(default=True, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=datetime.now, editable=True)

    def __str__(self):
        return self.name

    @property
    def osses(self):
        osses = []
        if self.mac:
            osses.append("Mac")
        if self.windows:
            osses.append("Windows")
        if self.linux:
            osses.append("Linux")
        return osses

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Software"
