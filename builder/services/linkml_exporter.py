import tempfile
from pathlib import Path

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model.meta import SchemaDefinition
from linkml_runtime.loaders import yaml_loader

from .linkml_builder import LinkMLBuilder


class ExportValidationError(Exception):
    def __init__(self, messages: list[str]):
        self.messages = messages
        super().__init__("; ".join(messages))


class LinkMLExporter:
    def __init__(self):
        self.builder = LinkMLBuilder()

    def export_yaml(self, template) -> str:
        schema = self.builder.build(template)
        yaml_str = yaml_dumper.dumps(schema)
        self._validate(yaml_str)
        return yaml_str

    def _validate(self, yaml_str: str) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_str)
            tmp_path = f.name

        try:
            yaml_loader.load(tmp_path, SchemaDefinition)
        except Exception as e:
            raise ExportValidationError([str(e)])
        finally:
            Path(tmp_path).unlink(missing_ok=True)
