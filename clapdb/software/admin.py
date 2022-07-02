from django.contrib import admin
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple
from .models import Developer, Category, Software, Feature


class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("name", "url",)
    readonly_fields = ("id",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence")
    prepopulated_fields = {"slug": ("name",)}


class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class SoftwareAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "developer", "category", "url", "free", "active")
    list_editable = ("category", "version", "url", "free", "active")
    list_filter = ("category", "active", "mac", "windows", "linux")
    search_fields = ("name", "developer__name", "free")
    save_as = True
    save_as_continue = False
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }



admin.site.register(Developer, DeveloperAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(Feature, FeatureAdmin)