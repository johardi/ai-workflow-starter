import uuid

from django.db import models
from slugify import slugify


class FormTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=400, blank=True, default="")
    schema_id = models.CharField(
        max_length=500, blank=True, default="", verbose_name="Schema URI"
    )
    description = models.TextField(blank=True, default="")
    license = models.CharField(max_length=200, blank=True, default="")
    prefixes = models.JSONField(default=dict, blank=True)
    imports = models.JSONField(default=list, blank=True)
    version = models.CharField(max_length=50, blank=True, default="0.1.0")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or self.name


class FormSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        FormTemplate, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=400, blank=True, default="")
    description = models.TextField(blank=True, default="")
    rank = models.IntegerField(default=0)
    is_root = models.BooleanField(default=False)

    class Meta:
        ordering = ["rank"]
        unique_together = [("template", "name")]

    def __str__(self):
        return self.title or self.name

    def save(self, *args, **kwargs):
        if not self.name and self.title:
            self.name = slugify(self.title, separator="_")
        super().save(*args, **kwargs)


class RangeType(models.TextChoices):
    STRING = "string", "Text"
    INTEGER = "integer", "Integer"
    FLOAT = "float", "Decimal"
    BOOLEAN = "boolean", "Boolean"
    DATE = "date", "Date"
    DATETIME = "datetime", "Date & Time"
    URI = "uri", "URI / Link"
    ENUM = "enum", "Choice (Enum)"
    OBJECT = "object", "Object Ref"


class FormField(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(
        FormSection, on_delete=models.CASCADE, related_name="fields"
    )
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=400, blank=True, default="")
    description = models.TextField(blank=True, default="")
    range_type = models.CharField(
        max_length=50, choices=RangeType.choices, default=RangeType.STRING
    )
    range_ref = models.CharField(max_length=200, blank=True, default="")
    required = models.BooleanField(default=False)
    multivalued = models.BooleanField(default=False)
    identifier = models.BooleanField(default=False)
    key = models.BooleanField(default=False)
    pattern = models.CharField(max_length=500, blank=True, default="")
    minimum_value = models.IntegerField(null=True, blank=True)
    maximum_value = models.IntegerField(null=True, blank=True)
    minimum_cardinality = models.IntegerField(null=True, blank=True)
    maximum_cardinality = models.IntegerField(null=True, blank=True)
    ifabsent = models.CharField(max_length=200, blank=True, default="")
    comments = models.JSONField(default=list, blank=True)
    annotations = models.JSONField(default=dict, blank=True)
    deprecated = models.CharField(max_length=300, blank=True, default="")
    rank = models.IntegerField(default=0)

    class Meta:
        ordering = ["rank"]
        unique_together = [("section", "name")]

    def __str__(self):
        return self.title or self.name

    def save(self, *args, **kwargs):
        if not self.name and self.title:
            self.name = slugify(self.title, separator="_")
        super().save(*args, **kwargs)


class EnumDefinition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        FormTemplate, on_delete=models.CASCADE, related_name="enums"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("template", "name")]

    def __str__(self):
        return self.name


class PermissibleValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enum_def = models.ForeignKey(
        EnumDefinition, on_delete=models.CASCADE, related_name="permissible_values"
    )
    value = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True, default="")
    meaning = models.CharField(max_length=500, blank=True, default="")
    rank = models.IntegerField(default=0)

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return self.value
