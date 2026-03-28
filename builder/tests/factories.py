from builder.models import (
    EnumDefinition,
    FormField,
    FormSection,
    FormTemplate,
    PermissibleValue,
)


def create_template(**kwargs):
    defaults = {
        "name": "test_form",
        "title": "Test Form",
        "schema_id": "https://example.org/test-form",
        "version": "0.1.0",
    }
    defaults.update(kwargs)
    return FormTemplate.objects.create(**defaults)


def create_section(template, **kwargs):
    defaults = {
        "name": "main_section",
        "title": "Main Section",
        "rank": 0,
        "is_root": True,
    }
    defaults.update(kwargs)
    return FormSection.objects.create(template=template, **defaults)


def create_field(section, **kwargs):
    defaults = {
        "name": "test_field",
        "title": "Test Field",
        "range_type": "string",
        "rank": 0,
    }
    defaults.update(kwargs)
    return FormField.objects.create(section=section, **defaults)


def create_enum(template, name="status", values=None):
    enum_def = EnumDefinition.objects.create(template=template, name=name)
    if values is None:
        values = [("active", "Active"), ("inactive", "Inactive")]
    for i, (val, desc) in enumerate(values):
        PermissibleValue.objects.create(
            enum_def=enum_def, value=val, description=desc, rank=i
        )
    return enum_def
