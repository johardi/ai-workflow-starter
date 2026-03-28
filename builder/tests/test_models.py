import pytest

from builder.models import FormField, FormSection, FormTemplate
from .factories import create_field, create_section, create_template


@pytest.mark.django_db
class TestFormTemplate:
    def test_create_template(self):
        t = create_template()
        assert str(t) == "Test Form"
        assert t.prefixes == {}
        assert t.imports == []

    def test_ordering(self):
        create_template(name="first")
        t2 = create_template(name="second")
        templates = list(FormTemplate.objects.all())
        assert templates[0] == t2  # Most recently updated first


@pytest.mark.django_db
class TestFormSection:
    def test_auto_slugify_name(self):
        t = create_template()
        s = FormSection.objects.create(template=t, title="My Section Title", rank=0)
        assert s.name == "my_section_title"

    def test_unique_together(self):
        t = create_template()
        create_section(t, name="unique")
        with pytest.raises(Exception):
            create_section(t, name="unique")


@pytest.mark.django_db
class TestFormField:
    def test_auto_slugify_name(self):
        t = create_template()
        s = create_section(t)
        f = FormField.objects.create(
            section=s, title="Full Name", range_type="string", rank=0
        )
        assert f.name == "full_name"

    def test_cascade_delete(self):
        t = create_template()
        s = create_section(t)
        create_field(s)
        assert FormField.objects.count() == 1
        s.delete()
        assert FormField.objects.count() == 0

    def test_json_field_defaults(self):
        t = create_template()
        s = create_section(t)
        f = create_field(s)
        assert f.comments == []
        assert f.annotations == {}
