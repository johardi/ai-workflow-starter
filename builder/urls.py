from django.urls import path

from . import views

app_name = "builder"

urlpatterns = [
    # Template list + create
    path("", views.TemplateListView.as_view(), name="list"),
    path("new/", views.TemplateCreateView.as_view(), name="create"),
    path("<uuid:pk>/delete/", views.TemplateDeleteView.as_view(), name="delete"),
    # Builder view (3-panel)
    path("<uuid:pk>/", views.BuilderView.as_view(), name="builder"),
    # Template settings
    path("<uuid:pk>/settings/", views.TemplateSettingsView.as_view(), name="settings"),
    # Preview + export
    path("<uuid:pk>/preview/", views.PreviewView.as_view(), name="preview"),
    path("<uuid:pk>/export/", views.ExportView.as_view(), name="export"),
    # Sections
    path(
        "<uuid:pk>/sections/", views.SectionCreateView.as_view(), name="section_create"
    ),
    path(
        "<uuid:pk>/sections/<uuid:sid>/",
        views.SectionUpdateView.as_view(),
        name="section_update",
    ),
    path(
        "<uuid:pk>/sections/<uuid:sid>/delete/",
        views.SectionDeleteView.as_view(),
        name="section_delete",
    ),
    # Fields
    path(
        "<uuid:pk>/sections/<uuid:sid>/fields/",
        views.FieldCreateView.as_view(),
        name="field_create",
    ),
    path(
        "<uuid:pk>/sections/<uuid:sid>/fields/<uuid:fid>/",
        views.FieldDetailView.as_view(),
        name="field_detail",
    ),
    path(
        "<uuid:pk>/sections/<uuid:sid>/fields/<uuid:fid>/copy/",
        views.FieldCopyView.as_view(),
        name="field_copy",
    ),
    # Reorder
    path("<uuid:pk>/reorder/", views.ReorderView.as_view(), name="reorder"),
    # Enums
    path("<uuid:pk>/enums/", views.EnumListCreateView.as_view(), name="enum_list"),
    path(
        "<uuid:pk>/enums/<uuid:eid>/",
        views.EnumDetailView.as_view(),
        name="enum_detail",
    ),
]
