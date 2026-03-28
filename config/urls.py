from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("forms/", include("builder.urls")),
    path("", RedirectView.as_view(url="/forms/", permanent=False)),
]
