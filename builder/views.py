import json

from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView
from slugify import slugify

from .forms import (
    EnumForm,
    FieldAdvancedForm,
    FieldBasicForm,
    FieldConstraintsForm,
    PermissibleValueFormSet,
    SectionForm,
    TemplateSettingsForm,
)
from .models import (
    EnumDefinition,
    FormField,
    FormSection,
    FormTemplate,
    RangeType,
)
from .services.linkml_exporter import ExportValidationError, LinkMLExporter


# --- Template list and create ---


class TemplateListView(ListView):
    model = FormTemplate
    template_name = "builder/template_list.html"
    context_object_name = "templates"


class TemplateCreateView(View):
    def post(self, request):
        count = FormTemplate.objects.count()
        name = f"form_{count + 1}"
        template = FormTemplate.objects.create(
            name=name,
            title="Untitled Form",
        )
        FormSection.objects.create(
            template=template,
            name="main",
            title="Main Section",
            rank=0,
            is_root=True,
        )
        return redirect("builder:builder", pk=template.pk)


class TemplateDeleteView(View):
    def post(self, request, pk):
        template = get_object_or_404(FormTemplate, pk=pk)
        template.delete()
        return redirect("builder:list")


# --- Builder (3-panel view) ---


class BuilderView(DetailView):
    model = FormTemplate
    template_name = "builder/builder.html"
    context_object_name = "template"

    def get_queryset(self):
        return FormTemplate.objects.prefetch_related(
            "sections__fields", "enums__permissible_values"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["range_types"] = RangeType.choices
        ctx["sections"] = self.object.sections.all()
        ctx["enums"] = self.object.enums.all()
        ctx["settings_form"] = TemplateSettingsForm(instance=self.object)
        return ctx


# --- Template settings (HTMX PUT) ---


class TemplateSettingsView(View):
    def put(self, request, pk):
        template = get_object_or_404(FormTemplate, pk=pk)
        from django.http import QueryDict

        data = QueryDict(request.body)
        form = TemplateSettingsForm(data, instance=template)
        if form.is_valid():
            # Handle name auto-generation from title
            template = form.save(commit=False)
            if data.get("title"):
                template.name = slugify(data["title"], separator="_")
            template.save()
            return render(
                request, "builder/partials/toast.html", {"message": "Settings saved"}
            )
        return render(
            request,
            "builder/partials/settings_modal.html",
            {
                "template": template,
                "settings_form": form,
            },
            status=422,
        )

    def get(self, request, pk):
        template = get_object_or_404(FormTemplate, pk=pk)
        form = TemplateSettingsForm(instance=template)
        return render(
            request,
            "builder/partials/settings_modal.html",
            {
                "template": template,
                "settings_form": form,
            },
        )


# --- Preview ---


class PreviewView(DetailView):
    model = FormTemplate
    template_name = "builder/preview.html"
    context_object_name = "template"

    def get_queryset(self):
        return FormTemplate.objects.prefetch_related(
            "sections__fields", "enums__permissible_values"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sections"] = self.object.sections.all()
        # Build enum lookup for preview
        enum_lookup = {}
        for enum in self.object.enums.all():
            enum_lookup[enum.name] = list(
                enum.permissible_values.values("value", "description")
            )
        ctx["enum_lookup"] = enum_lookup
        return ctx


# --- Export ---


class ExportView(View):
    def get(self, request, pk):
        template = get_object_or_404(
            FormTemplate.objects.prefetch_related(
                "sections__fields", "enums__permissible_values"
            ),
            pk=pk,
        )
        exporter = LinkMLExporter()
        try:
            yaml_str = exporter.export_yaml(template)
        except ExportValidationError as e:
            return JsonResponse({"errors": e.messages}, status=422)
        response = HttpResponse(yaml_str, content_type="application/x-yaml")
        response["Content-Disposition"] = f'attachment; filename="{template.name}.yaml"'
        return response


# --- Section CRUD ---


class SectionCreateView(View):
    def post(self, request, pk):
        template = get_object_or_404(FormTemplate, pk=pk)
        max_rank = template.sections.count()
        section = FormSection.objects.create(
            template=template,
            name=f"section_{max_rank + 1}",
            title=f"Section {max_rank + 1}",
            rank=max_rank,
            is_root=False,
        )
        return render(
            request,
            "builder/partials/section_card.html",
            {
                "section": section,
                "template": template,
            },
        )


class SectionDeleteView(View):
    def delete(self, request, pk, sid):
        section = get_object_or_404(FormSection, pk=sid, template_id=pk)
        section.delete()
        return HttpResponse("")


class SectionUpdateView(View):
    def put(self, request, pk, sid):
        section = get_object_or_404(FormSection, pk=sid, template_id=pk)
        from django.http import QueryDict

        data = QueryDict(request.body)
        form = SectionForm(data, instance=section)
        if form.is_valid():
            section = form.save(commit=False)
            if not section.name or section.name.startswith("section_"):
                section.name = slugify(section.title, separator="_")
            section.save()
            return render(
                request,
                "builder/partials/section_card.html",
                {
                    "section": section,
                    "template": section.template,
                },
            )
        return HttpResponse(status=422)


# --- Field CRUD ---


class FieldCreateView(View):
    def post(self, request, pk, sid):
        section = get_object_or_404(FormSection, pk=sid, template_id=pk)
        range_type = request.POST.get("range_type", "string")
        max_rank = section.fields.count()
        label = dict(RangeType.choices).get(range_type, "Field")
        # Generate unique name
        counter = max_rank + 1
        name = f"field_{counter}"
        while section.fields.filter(name=name).exists():
            counter += 1
            name = f"field_{counter}"
        field = FormField.objects.create(
            section=section,
            name=name,
            title=f"New {label}",
            range_type=range_type,
            rank=max_rank,
        )
        return render(
            request,
            "builder/partials/field_row.html",
            {
                "field": field,
                "template": section.template,
            },
        )


class FieldDetailView(View):
    def get(self, request, pk, sid, fid):
        field = get_object_or_404(
            FormField, pk=fid, section_id=sid, section__template_id=pk
        )
        template = field.section.template
        return render(
            request,
            "builder/partials/config_panel.html",
            {
                "field": field,
                "template": template,
                "basic_form": FieldBasicForm(instance=field),
                "constraints_form": FieldConstraintsForm(
                    instance=field, template=template
                ),
                "advanced_form": FieldAdvancedForm(instance=field),
                "enums": template.enums.all(),
                "sections": template.sections.all(),
            },
        )

    def put(self, request, pk, sid, fid):
        field = get_object_or_404(
            FormField, pk=fid, section_id=sid, section__template_id=pk
        )
        template = field.section.template
        from django.http import QueryDict

        data = QueryDict(request.body)

        tab = data.get("_tab", "basic")
        if tab == "basic":
            form = FieldBasicForm(data, instance=field)
        elif tab == "constraints":
            form = FieldConstraintsForm(data, instance=field, template=template)
        else:
            form = FieldAdvancedForm(data, instance=field)

        if form.is_valid():
            form.save()
            field.refresh_from_db()
            # Return updated field row for the canvas
            response = render(
                request,
                "builder/partials/field_row.html",
                {
                    "field": field,
                    "template": template,
                },
            )
            response["HX-Trigger"] = "fieldUpdated"
            return response
        return render(
            request,
            "builder/partials/config_panel.html",
            {
                "field": field,
                "template": template,
                "basic_form": FieldBasicForm(instance=field)
                if tab != "basic"
                else form,
                "constraints_form": FieldConstraintsForm(
                    instance=field, template=template
                )
                if tab != "constraints"
                else form,
                "advanced_form": FieldAdvancedForm(instance=field)
                if tab != "advanced"
                else form,
                "enums": template.enums.all(),
                "sections": template.sections.all(),
            },
            status=422,
        )

    def delete(self, request, pk, sid, fid):
        field = get_object_or_404(
            FormField, pk=fid, section_id=sid, section__template_id=pk
        )
        field.delete()
        return HttpResponse("")


class FieldCopyView(View):
    def post(self, request, pk, sid, fid):
        source = get_object_or_404(
            FormField, pk=fid, section_id=sid, section__template_id=pk
        )
        section = source.section
        template = section.template

        # Shift ranks to make room after source
        new_rank = source.rank + 1
        section.fields.filter(rank__gte=new_rank).update(rank=models.F("rank") + 1)

        # Generate unique name
        base_name = source.name + "_copy"
        name = base_name
        counter = 2
        while section.fields.filter(name=name).exists():
            name = f"{base_name}_{counter}"
            counter += 1

        # Clone the field
        source.pk = None
        source.name = name
        source.title = (source.title or "") + " (copy)"
        source.rank = new_rank
        source.save()

        return render(
            request,
            "builder/partials/field_row.html",
            {
                "field": source,
                "template": template,
            },
        )


# --- Reorder ---


class ReorderView(View):
    def post(self, request, pk):
        get_object_or_404(FormTemplate, pk=pk)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        items = data.get("items", [])
        for item in items:
            FormField.objects.filter(pk=item["id"]).update(
                section_id=item.get("section_id", None) or None,
                rank=item["rank"],
            )
        return HttpResponse(status=204)


# --- Enum CRUD ---


class EnumListCreateView(View):
    def get(self, request, pk):
        template = get_object_or_404(FormTemplate, pk=pk)
        enums = template.enums.prefetch_related("permissible_values").all()
        mode = request.GET.get("mode", "full")

        if mode == "palette":
            return render(
                request,
                "builder/partials/enum_palette_list.html",
                {
                    "template": template,
                    "enums": enums,
                },
            )
        elif mode == "form":
            return render(
                request,
                "builder/partials/enum_form.html",
                {
                    "template": template,
                    "enum_form": EnumForm(),
                    "pv_formset": PermissibleValueFormSet(),
                },
            )
        elif mode == "select":
            return render(
                request,
                "builder/partials/enum_select.html",
                {
                    "template": template,
                    "enums": enums,
                },
            )
        return render(
            request,
            "builder/partials/enum_editor.html",
            {
                "template": template,
                "enums": enums,
            },
        )

    def post(self, request, pk):
        template = get_object_or_404(FormTemplate, pk=pk)
        form = EnumForm(request.POST)
        if form.is_valid():
            enum = form.save(commit=False)
            enum.template = template
            enum.save()
            formset = PermissibleValueFormSet(request.POST, instance=enum)
            if formset.is_valid():
                formset.save()
            response = render(
                request,
                "builder/partials/enum_form.html",
                {
                    "template": template,
                    "enum": enum,
                    "enum_form": EnumForm(instance=enum),
                    "pv_formset": PermissibleValueFormSet(instance=enum),
                    "saved": True,
                },
            )
            response["HX-Trigger"] = "enumListChanged"
            return response
        return render(
            request,
            "builder/partials/enum_form.html",
            {
                "template": template,
                "enum_form": form,
                "pv_formset": PermissibleValueFormSet(request.POST),
            },
            status=422,
        )


class EnumDetailView(View):
    def get(self, request, pk, eid):
        template = get_object_or_404(FormTemplate, pk=pk)
        enum = get_object_or_404(EnumDefinition, pk=eid, template=template)
        mode = request.GET.get("mode", "full")

        if mode == "form":
            return render(
                request,
                "builder/partials/enum_form.html",
                {
                    "template": template,
                    "enum": enum,
                    "enum_form": EnumForm(instance=enum),
                    "pv_formset": PermissibleValueFormSet(instance=enum),
                },
            )
        formset = PermissibleValueFormSet(instance=enum)
        return render(
            request,
            "builder/partials/enum_editor.html",
            {
                "template": template,
                "enum": enum,
                "enums": template.enums.prefetch_related("permissible_values").all(),
                "pv_formset": formset,
            },
        )

    def post(self, request, pk, eid):
        template = get_object_or_404(FormTemplate, pk=pk)
        enum = get_object_or_404(EnumDefinition, pk=eid, template=template)
        form = EnumForm(request.POST, instance=enum)
        if form.is_valid():
            form.save()
        formset = PermissibleValueFormSet(request.POST, instance=enum)
        if formset.is_valid():
            formset.save()
        response = render(
            request,
            "builder/partials/enum_form.html",
            {
                "template": template,
                "enum": enum,
                "enum_form": EnumForm(instance=enum),
                "pv_formset": PermissibleValueFormSet(instance=enum),
                "saved": True,
            },
        )
        response["HX-Trigger"] = "enumListChanged"
        return response

    def delete(self, request, pk, eid):
        enum = get_object_or_404(EnumDefinition, pk=eid, template_id=pk)
        enum.delete()
        response = HttpResponse("")
        response["HX-Trigger"] = "enumListChanged"
        return response
