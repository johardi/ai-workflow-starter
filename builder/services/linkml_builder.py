from linkml_runtime.linkml_model.meta import (
    Annotation,
    ClassDefinition,
    EnumDefinition as LinkMLEnumDefinition,
    PermissibleValue as LinkMLPermissibleValue,
    Prefix,
    SchemaDefinition,
    SlotDefinition,
)


PRIMITIVE_RANGES = {
    "string": "string",
    "integer": "integer",
    "float": "float",
    "boolean": "boolean",
    "date": "date",
    "datetime": "datetime",
    "uri": "uri",
}


class LinkMLBuilder:
    def build(self, template) -> SchemaDefinition:
        schema = SchemaDefinition(
            id=template.schema_id or f"https://example.org/{template.name}",
            name=template.name,
            title=template.title or None,
            description=template.description or None,
            license=template.license or None,
            version=template.version or None,
        )

        # Prefixes
        for prefix_name, prefix_ref in (template.prefixes or {}).items():
            schema.prefixes[prefix_name] = Prefix(
                prefix_prefix=prefix_name, prefix_reference=prefix_ref
            )
        if "linkml" not in schema.prefixes:
            schema.prefixes["linkml"] = Prefix(
                prefix_prefix="linkml",
                prefix_reference="https://w3id.org/linkml/",
            )

        # Imports
        imports = list(template.imports or [])
        if "linkml:types" not in imports:
            imports.insert(0, "linkml:types")
        schema.imports = imports

        # Enums
        for enum_row in template.enums.all().prefetch_related("permissible_values"):
            linkml_enum = LinkMLEnumDefinition(
                name=enum_row.name,
                description=enum_row.description or None,
            )
            for pv in enum_row.permissible_values.all():
                linkml_pv = LinkMLPermissibleValue(
                    text=pv.value,
                    description=pv.description or None,
                    meaning=pv.meaning or None,
                )
                linkml_enum.permissible_values[pv.value] = linkml_pv
            schema.enums[enum_row.name] = linkml_enum

        # Classes and slots
        sections = template.sections.all().prefetch_related("fields")
        for section in sections:
            cls = ClassDefinition(
                name=section.name,
                title=section.title or None,
                description=section.description or None,
                tree_root=section.is_root or None,
            )

            for field in section.fields.all():
                slot = self._build_slot(field)
                cls.attributes[field.name] = slot

            schema.classes[section.name] = cls

        return schema

    def _build_slot(self, field) -> SlotDefinition:
        # Determine range
        if field.range_type in PRIMITIVE_RANGES:
            range_val = PRIMITIVE_RANGES[field.range_type]
        elif field.range_type in ("enum", "object"):
            range_val = field.range_ref or "string"
        else:
            range_val = "string"

        slot = SlotDefinition(
            name=field.name,
            title=field.title or None,
            description=field.description or None,
            range=range_val,
            required=field.required or None,
            multivalued=field.multivalued or None,
            identifier=field.identifier or None,
            key=field.key or None,
            pattern=field.pattern or None,
            minimum_value=field.minimum_value,
            maximum_value=field.maximum_value,
            minimum_cardinality=field.minimum_cardinality,
            maximum_cardinality=field.maximum_cardinality,
            ifabsent=field.ifabsent or None,
            deprecated=field.deprecated or None,
            rank=field.rank if field.rank else None,
        )

        # Comments (help text)
        if field.comments:
            slot.comments = list(field.comments)

        # Annotations
        if field.annotations:
            for ann_key, ann_val in field.annotations.items():
                slot.annotations[ann_key] = Annotation(tag=ann_key, value=str(ann_val))

        return slot
