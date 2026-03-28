import pytest
import yaml

from builder.services.linkml_builder import LinkMLBuilder
from builder.services.linkml_exporter import LinkMLExporter
from .factories import create_enum, create_field, create_section, create_template


@pytest.mark.django_db
class TestLinkMLBuilder:
    def _build(self, template):
        return LinkMLBuilder().build(template)

    def test_basic_schema_structure(self):
        t = create_template()
        s = create_section(t)
        create_field(s, name="full_name", title="Full Name", range_type="string")

        schema = self._build(t)

        assert schema.name == "test_form"
        assert schema.id == "https://example.org/test-form"
        assert "linkml:types" in schema.imports
        assert "linkml" in schema.prefixes
        assert "main_section" in schema.classes
        cls = schema.classes["main_section"]
        assert cls.tree_root is True
        assert "full_name" in cls.attributes

    def test_all_primitive_range_types(self):
        t = create_template(name="primitives_form")
        s = create_section(t)
        primitives = [
            "string",
            "integer",
            "float",
            "boolean",
            "date",
            "datetime",
            "uri",
        ]
        for i, rt in enumerate(primitives):
            create_field(s, name=f"field_{rt}", range_type=rt, rank=i)

        schema = self._build(t)
        cls = schema.classes["main_section"]

        for rt in primitives:
            slot = cls.attributes[f"field_{rt}"]
            assert slot.range == rt

    def test_enum_range_type(self):
        t = create_template(name="enum_form")
        s = create_section(t)
        create_enum(t, name="color_enum", values=[("red", "Red"), ("blue", "Blue")])
        create_field(s, name="color", range_type="enum", range_ref="color_enum", rank=0)

        schema = self._build(t)

        assert "color_enum" in schema.enums
        enum = schema.enums["color_enum"]
        assert "red" in enum.permissible_values
        assert "blue" in enum.permissible_values
        assert enum.permissible_values["red"].description == "Red"

        cls = schema.classes["main_section"]
        assert cls.attributes["color"].range == "color_enum"

    def test_object_range_type(self):
        t = create_template(name="obj_form")
        s1 = create_section(t, name="person", title="Person")
        s2 = create_section(t, name="address", title="Address", rank=1, is_root=False)
        create_field(s1, name="home_address", range_type="object", range_ref="address")
        create_field(s2, name="street", range_type="string")

        schema = self._build(t)

        assert "person" in schema.classes
        assert "address" in schema.classes
        assert schema.classes["person"].attributes["home_address"].range == "address"

    def test_field_constraints(self):
        t = create_template(name="constraints_form")
        s = create_section(t)
        create_field(
            s,
            name="email",
            range_type="string",
            required=True,
            pattern=r"^[\w.-]+@[\w.-]+\.\w+$",
            minimum_cardinality=1,
            maximum_cardinality=1,
        )

        schema = self._build(t)
        slot = schema.classes["main_section"].attributes["email"]

        assert slot.required is True
        assert slot.pattern == r"^[\w.-]+@[\w.-]+\.\w+$"
        assert slot.minimum_cardinality == 1
        assert slot.maximum_cardinality == 1

    def test_numeric_constraints(self):
        t = create_template(name="numeric_form")
        s = create_section(t)
        create_field(
            s,
            name="age",
            range_type="integer",
            minimum_value=0,
            maximum_value=150,
        )

        schema = self._build(t)
        slot = schema.classes["main_section"].attributes["age"]

        assert slot.minimum_value == 0
        assert slot.maximum_value == 150

    def test_annotations_and_comments(self):
        t = create_template(name="ann_form")
        s = create_section(t)
        create_field(
            s,
            name="notes",
            comments=["Enter your notes here"],
            annotations={"placeholder": "Type something..."},
        )

        schema = self._build(t)
        slot = schema.classes["main_section"].attributes["notes"]

        assert slot.comments == ["Enter your notes here"]
        assert "placeholder" in slot.annotations

    def test_advanced_slot_properties(self):
        t = create_template(name="adv_form")
        s = create_section(t)
        create_field(
            s,
            name="record_id",
            identifier=True,
            ifabsent="string(AUTO)",
            deprecated="Use new_id instead",
        )

        schema = self._build(t)
        slot = schema.classes["main_section"].attributes["record_id"]

        assert slot.identifier is True
        assert slot.ifabsent == "string(AUTO)"
        assert slot.deprecated == "Use new_id instead"

    def test_multivalued_field(self):
        t = create_template(name="multi_form")
        s = create_section(t)
        create_field(s, name="tags", multivalued=True)

        schema = self._build(t)
        slot = schema.classes["main_section"].attributes["tags"]
        assert slot.multivalued is True

    def test_custom_prefixes_and_imports(self):
        t = create_template(
            name="prefix_form",
            prefixes={"schema": "http://schema.org/"},
            imports=["linkml:types", "other:schema"],
        )
        s = create_section(t)
        create_field(s, name="dummy")

        schema = self._build(t)

        assert "schema" in schema.prefixes
        assert "linkml:types" in schema.imports
        assert "other:schema" in schema.imports


@pytest.mark.django_db
class TestLinkMLExporter:
    def test_export_yaml_round_trip(self):
        t = create_template(name="export_test")
        s = create_section(t)
        create_field(s, name="name", title="Name", range_type="string", required=True)
        create_field(s, name="age", range_type="integer", rank=1)

        exporter = LinkMLExporter()
        yaml_str = exporter.export_yaml(t)

        # Verify it's valid YAML
        data = yaml.safe_load(yaml_str)
        assert data["name"] == "export_test"
        assert "classes" in data

    def test_export_with_enum(self):
        t = create_template(name="enum_export")
        s = create_section(t)
        create_enum(
            t, name="status_enum", values=[("open", "Open"), ("closed", "Closed")]
        )
        create_field(s, name="status", range_type="enum", range_ref="status_enum")

        yaml_str = LinkMLExporter().export_yaml(t)
        data = yaml.safe_load(yaml_str)

        assert "enums" in data
        assert "status_enum" in data["enums"]
