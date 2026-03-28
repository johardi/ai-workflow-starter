from django.contrib import admin

from .models import (
    EnumDefinition,
    FormField,
    FormSection,
    FormTemplate,
    PermissibleValue,
)


class FormSectionInline(admin.TabularInline):
    model = FormSection
    extra = 0


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 0


class PermissibleValueInline(admin.TabularInline):
    model = PermissibleValue
    extra = 0


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "version", "updated_at"]
    inlines = [FormSectionInline]


@admin.register(FormSection)
class FormSectionAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "template", "rank", "is_root"]
    inlines = [FormFieldInline]


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "range_type", "required", "section"]


@admin.register(EnumDefinition)
class EnumDefinitionAdmin(admin.ModelAdmin):
    list_display = ["name", "template"]
    inlines = [PermissibleValueInline]
