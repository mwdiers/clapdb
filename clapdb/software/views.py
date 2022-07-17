import operator
from functools import reduce
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Lower
from django.utils import timezone as tz
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django import forms
from django.conf import settings
from django.contrib.syndication.views import Feed
from .models import Category, Software, Developer, Feature


def home(request):
    recent_updates = Software\
        .objects.select_related("developer", "category")\
        .filter(created__gte=tz.now()-tz.timedelta(days=settings.CDB_RECENT_UPDATES_DAYS))\
        .filter(active=True)\
        .order_by("-created")[:settings.CDB_RECENT_UPDATES_MAX]
    context = {
        "recent_updates": recent_updates,
    }
    return render(request, 'home.html', context=context)


def stats(request):
    context = {
        "categories": Category.objects.annotate(software_count=Count("software")).order_by("sequence"),
        "developer_count": Developer.objects.count(),
        "software_count": Software.objects.count(),
        "free_count": Software.objects.filter(free=True).count(),
    }
    return render(request, "software/stats.html", context=context)


class SoftwareDetailView(DetailView):
    model = Software
    template_name = "software/software.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["osses"] = ", ".join(self.object.osses)
        return context


class CategoryListView(ListView):
    model = Software
    template_name = "software/software_list.html"

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset().select_related("developer").order_by(Lower("developer__name"), Lower("name")).filter(active=True)
        if "slug" in self.kwargs:
            qs = qs.filter(category__slug=self.kwargs["slug"])
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "slug" in self.kwargs:
            context["category"] = Category.objects.get(slug=self.kwargs["slug"])
        return context


# For retrieving data with autocomplete.js
def get_developers():
    result = Developer.objects.order_by(Lower("name")).values_list("name", flat=True).distinct()
    return JsonResponse({"status": 200, "data": result})


class SearchForm(forms.Form):
    developer = forms.CharField(label="developer", max_length=50, required=False)
    title = forms.CharField(label="software", max_length=50, required=False)
    category = forms.ModelChoiceField(label="category", required=False, empty_label="All",
                                      queryset=Category.objects.order_by("sequence"))
    free = forms.BooleanField(label="Free", required=False)
    mac = forms.BooleanField(label="Mac", required=False)
    windows = forms.BooleanField(label="Windows", required=False)
    linux = forms.BooleanField(label="Linux", required=False)
    features = forms.MultipleChoiceField(choices=[(x.pk, x.name) for x in Feature.objects.all()],
                                         widget=forms.CheckboxSelectMultiple, required=False)


class SearchView(FormView):
    template_name = "software/search.html"
    form_class = SearchForm
    success_url = reverse_lazy("search")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # Check for form input
            is_data = False
            for k, v in cleaned_data.items():
                if v:
                    is_data = True

            if is_data:
                # Cannot use Q objects in this case because it leads to impossible WHERE clause when more then
                # one feature is chosen.
                software = Software.objects.filter(active=True)
                if cleaned_data["features"]:
                    for feature in Feature.objects.filter(pk__in=cleaned_data["features"]):
                        software = software.filter(features=feature)

                query = Q(active=True)
                if cleaned_data["developer"]:
                    query &= Q(developer__name__icontains=cleaned_data["developer"])
                if cleaned_data["category"]:
                    query &= Q(category=cleaned_data["category"])
                if cleaned_data["title"]:
                    query &= Q(name__icontains=cleaned_data["title"])
                if cleaned_data["free"]:
                    query &= Q(free=True)
                if cleaned_data["mac"]:
                    query &= Q(mac=True)
                if cleaned_data["windows"]:
                    query &= Q(windows=True)
                if cleaned_data["linux"]:
                    query &= Q(linux=True)

                software = software.filter(query).distinct()

                if software.count():
                    software = software.order_by(Lower("developer__name"), "category__sequence", Lower("name"))
                else:
                    software = None
            else:
                software = None

            self.extra_context = {"software": software,
                                  "search": True,
                                  "s_developer": cleaned_data["developer"],
                                  "s_category": cleaned_data["category"].id if cleaned_data["category"] else None,
                                  "s_title": cleaned_data["title"],
                                  "s_free": cleaned_data["free"],
                                  "s_mac": cleaned_data["mac"],
                                  "s_windows": cleaned_data["windows"],
                                  "s_linux": cleaned_data["linux"],
                                  "s_features": [int(x) for x in cleaned_data["features"]]}

        return super().get(request, *args, **kwargs)


class DeveloperDetailView(DetailView):
    model = Developer
    template_name = "software/developer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["software_list"] = self.object.software_set.all().order_by("category", "name")
        return context


class DeveloperListView(ListView):
    model = Developer


class RecentUpdatesFeed(Feed):
    title = "CLAPdb Recent Updates"
    link = "/"
    description = "CLAP Audio Software Database Recent Updates"

    def items(self):
        return Software\
            .objects.select_related("developer", "category")\
            .filter(created__gte=tz.now()-tz.timedelta(days=settings.CDB_RECENT_UPDATES_DAYS))\
            .filter(active=True)\
            .order_by("-created")[:settings.CDB_RECENT_UPDATES_MAX]

    def item_title(self, item):
        return f"{item.created.strftime('%Y-%m-%d')} &mdash; {item.developer.name} {item.name}"

    def item_description(self, item):
        desc = f"""
        <p>Developer: {item.developer.name}</p>
        <p>Title: {item.name}</p>
        <p>Version: {item.version}</p>
        <p>URL: <a href='{item.url}'>{item.url}</a>
        """
        if item.notes:
            desc = desc + f"\n<p>Notes:</p>{item.notes}"
        return desc

    def item_link(self, item):
        return reverse('software', args=[item.pk])

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.updated
