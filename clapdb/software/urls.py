from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("software/<int:pk>/", views.SoftwareDetailView.as_view(), name="software",),
    path("developer/<slug:slug>", views.DeveloperDetailView.as_view(), name="developer", ),
    path("developers/", views.DeveloperListView.as_view(), name="developer-list", ),
    path("category/<slug:slug>", views.CategoryListView.as_view(), name="software-list-category"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("stats/", views.stats, name="stats"),
    path("feed/", views.RecentUpdatesFeed()),
]
