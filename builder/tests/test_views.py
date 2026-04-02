import json

import pytest
from django.test import Client

from builder.models import FormSection, FormTemplate
from .factories import create_enum, create_field, create_section, create_template


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def template_with_field(db):
    t = create_template()
    s = create_section(t)
    f = create_field(s)
    return t, s, f


@pytest.mark.django_db
class TestTemplateListView:
    def test_empty_list(self, client):
        resp = client.get("/forms/")
        assert resp.status_code == 200
        assert b"No forms yet" in resp.content

    def test_list_with_templates(self, client, template_with_field):
        resp = client.get("/forms/")
        assert resp.status_code == 200
        assert b"Test Form" in resp.content


@pytest.mark.django_db
class TestTemplateCreateView:
    def test_create_template(self, client):
        resp = client.post("/forms/new/")
        assert resp.status_code == 302
        t = FormTemplate.objects.first()
        assert t is not None
        assert t.title == "Untitled Form"
        assert t.sections.count() == 1
        assert t.sections.first().is_root is True


@pytest.mark.django_db
class TestTemplateDeleteView:
    def test_delete_template(self, client):
        template = create_template()
        section = create_section(template)
        create_field(section)
        enum_def = create_enum(template)

        resp = client.post(f"/forms/{template.pk}/delete/")

        assert resp.status_code == 302
        assert resp.headers["Location"] == "/forms/"
        assert FormTemplate.objects.filter(pk=template.pk).count() == 0
        assert FormSection.objects.filter(pk=section.pk).count() == 0
        assert template.enums.filter(pk=enum_def.pk).count() == 0


@pytest.mark.django_db
class TestBuilderView:
    def test_builder_page(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.get(f"/forms/{t.pk}/")
        assert resp.status_code == 200
        assert b"Field Settings" not in resp.content  # No field selected yet
        assert bytes(str(f.title), "utf-8") in resp.content


@pytest.mark.django_db
class TestFieldCRUD:
    def test_create_field(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.post(
            f"/forms/{t.pk}/sections/{s.pk}/fields/",
            {"range_type": "integer"},
        )
        assert resp.status_code == 200
        assert s.fields.count() == 2

    def test_get_field_config(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.get(f"/forms/{t.pk}/sections/{s.pk}/fields/{f.pk}/")
        assert resp.status_code == 200
        assert b"Field Settings" in resp.content

    def test_update_field(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.put(
            f"/forms/{t.pk}/sections/{s.pk}/fields/{f.pk}/",
            "_tab=basic&title=Updated+Title&name=updated_title&description=&required=on&multivalued=&help_text=&placeholder=",
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        f.refresh_from_db()
        assert f.title == "Updated Title"
        assert f.required is True

    def test_delete_field(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.delete(f"/forms/{t.pk}/sections/{s.pk}/fields/{f.pk}/")
        assert resp.status_code == 200
        assert s.fields.count() == 0


@pytest.mark.django_db
class TestSectionCRUD:
    def test_create_section(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.post(f"/forms/{t.pk}/sections/")
        assert resp.status_code == 200
        assert t.sections.count() == 2

    def test_delete_section(self, client, template_with_field):
        t, s, f = template_with_field
        # Create a non-root section to delete
        s2 = FormSection.objects.create(
            template=t, name="extra", title="Extra", rank=1, is_root=False
        )
        resp = client.delete(f"/forms/{t.pk}/sections/{s2.pk}/delete/")
        assert resp.status_code == 200
        assert t.sections.count() == 1


@pytest.mark.django_db
class TestReorderView:
    def test_reorder_fields(self, client, template_with_field):
        t, s, f = template_with_field
        f2 = create_field(s, name="second_field", rank=1)
        resp = client.post(
            f"/forms/{t.pk}/reorder/",
            json.dumps(
                {
                    "items": [
                        {"id": str(f2.pk), "section_id": str(s.pk), "rank": 0},
                        {"id": str(f.pk), "section_id": str(s.pk), "rank": 1},
                    ]
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 204
        f.refresh_from_db()
        f2.refresh_from_db()
        assert f.rank == 1
        assert f2.rank == 0


@pytest.mark.django_db
class TestExportView:
    def test_export_yaml(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.get(f"/forms/{t.pk}/export/")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/x-yaml"
        assert b"name: test_form" in resp.content


@pytest.mark.django_db
class TestPreviewView:
    def test_preview_page(self, client, template_with_field):
        t, s, f = template_with_field
        resp = client.get(f"/forms/{t.pk}/preview/")
        assert resp.status_code == 200
        assert b"Preview only" in resp.content
        assert bytes(f.title, "utf-8") in resp.content
