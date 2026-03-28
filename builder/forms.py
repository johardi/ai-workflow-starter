from django import forms
from django.core.exceptions import ValidationError

from .models import (
    EnumDefinition,
    FormField,
    FormSection,
    FormTemplate,
    PermissibleValue,
    RangeType,
)


class TemplateSettingsForm(forms.ModelForm):
    class Meta:
        model = FormTemplate
        fields = [
            "title",
            "schema_id",
            "version",
            "license",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "schema_id": forms.TextInput(
                attrs={
                    "class": "w-full border rounded px-3 py-2",
                    "placeholder": "https://example.org/my-form",
                }
            ),
            "version": forms.TextInput(
                attrs={
                    "class": "w-full border rounded px-3 py-2",
                    "placeholder": "0.1.0",
                }
            ),
            "license": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "description": forms.Textarea(
                attrs={"class": "w-full border rounded px-3 py-2", "rows": 3}
            ),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = FormSection
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "description": forms.Textarea(
                attrs={"class": "w-full border rounded px-3 py-2", "rows": 2}
            ),
        }


class FieldBasicForm(forms.ModelForm):
    help_text = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 2, "class": "w-full border rounded px-3 py-2"}
        ),
    )
    placeholder = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
    )

    class Meta:
        model = FormField
        fields = [
            "title",
            "name",
            "description",
            "required",
            "multivalued",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "name": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2 font-mono text-sm"}
            ),
            "description": forms.Textarea(
                attrs={"class": "w-full border rounded px-3 py-2", "rows": 2}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["help_text"].initial = (
                self.instance.comments[0] if self.instance.comments else ""
            )
            self.fields["placeholder"].initial = self.instance.annotations.get(
                "placeholder", ""
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        help_text = self.cleaned_data.get("help_text", "")
        instance.comments = [help_text] if help_text else []
        placeholder = self.cleaned_data.get("placeholder", "")
        if placeholder:
            instance.annotations["placeholder"] = placeholder
        elif "placeholder" in instance.annotations:
            del instance.annotations["placeholder"]
        if commit:
            instance.save()
        return instance


class FieldConstraintsForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = [
            "pattern",
            "minimum_value",
            "maximum_value",
            "minimum_cardinality",
            "maximum_cardinality",
            "range_ref",
        ]
        widgets = {
            "pattern": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2 font-mono text-sm"}
            ),
            "minimum_value": forms.NumberInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "maximum_value": forms.NumberInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "minimum_cardinality": forms.NumberInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "maximum_cardinality": forms.NumberInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "range_ref": forms.Select(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
        }

    def __init__(self, *args, template=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.range_type == RangeType.ENUM:
            self.fields["range_ref"] = forms.ModelChoiceField(
                queryset=EnumDefinition.objects.filter(template=template)
                if template
                else EnumDefinition.objects.none(),
                to_field_name="name",
                required=False,
                widget=forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            )
        elif self.instance.pk and self.instance.range_type == RangeType.OBJECT:
            self.fields["range_ref"] = forms.ModelChoiceField(
                queryset=FormSection.objects.filter(template=template)
                if template
                else FormSection.objects.none(),
                to_field_name="name",
                required=False,
                widget=forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            )


class FieldAdvancedForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = [
            "identifier",
            "key",
            "ifabsent",
            "deprecated",
        ]
        widgets = {
            "ifabsent": forms.TextInput(
                attrs={"class": "w-full border rounded px-3 py-2"}
            ),
            "deprecated": forms.TextInput(
                attrs={
                    "class": "w-full border rounded px-3 py-2",
                    "placeholder": "Deprecation message",
                }
            ),
        }

    def clean_identifier(self):
        identifier = self.cleaned_data.get("identifier")
        if identifier and self.instance.pk:
            existing = FormField.objects.filter(
                section=self.instance.section,
                identifier=True,
            ).exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(
                    "Only one field per section can be an identifier."
                )
        return identifier


class EnumForm(forms.ModelForm):
    class Meta:
        model = EnumDefinition
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "description": forms.Textarea(
                attrs={"class": "w-full border rounded px-3 py-2", "rows": 2}
            ),
        }


class PermissibleValueForm(forms.ModelForm):
    class Meta:
        model = PermissibleValue
        fields = ["value", "description", "meaning", "rank"]
        widgets = {
            "value": forms.TextInput(
                attrs={
                    "class": "border rounded px-2 py-1",
                    "placeholder": "Label *",
                    "required": "required",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "border rounded px-2 py-1",
                    "placeholder": "Description",
                    "rows": 1,
                }
            ),
            "meaning": forms.TextInput(
                attrs={
                    "class": "border rounded px-2 py-1",
                    "placeholder": "Meaning (IRI)",
                }
            ),
            "rank": forms.HiddenInput(),
        }


PermissibleValueFormSet = forms.inlineformset_factory(
    EnumDefinition,
    PermissibleValue,
    form=PermissibleValueForm,
    extra=1,
    can_delete=True,
)
