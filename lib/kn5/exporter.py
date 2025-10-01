from __future__ import annotations

import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from .constants import KN5_HEADER, KN5_VERSION
from .kn5_writer import KN5Writer
from .material_writer import MaterialWriter
from .node_writer import NodeWriter
from .texture_writer import TextureWriter

if TYPE_CHECKING:
    from bpy.types import Context


class KN5Exporter(KN5Writer):
    """
    Main KN5 file exporter.

    Orchestrates writing of header, textures, materials, and scene hierarchy.
    """

    def __init__(self, file, context: Context, warnings: list[str]):
        super().__init__(file)
        self.context = context
        self.warnings = warnings

    def write(self) -> None:
        """Write complete KN5 file: header + textures + materials + nodes."""
        self._write_header()
        self._write_content()

    def _write_header(self) -> None:
        """Write KN5 file signature and version."""
        self.file.write(KN5_HEADER)
        self.write_uint(KN5_VERSION)

    def _write_content(self) -> None:
        """Write textures, materials, and scene hierarchy."""
        texture_writer = TextureWriter(self.file, self.context, self.warnings)
        texture_writer.write()

        material_writer = MaterialWriter(self.file, self.context, self.warnings)
        material_writer.write()

        node_writer = NodeWriter(self.file, self.context, material_writer, self.warnings)
        node_writer.write()


def export_kn5(filepath: str, context: Context) -> dict[str, str | list[str]]:
    """
    Export scene to KN5 file.

    Args:
        filepath: Output KN5 file path
        context: Blender context

    Returns:
        Dictionary with 'status' ('success' or 'error') and 'warnings' list
    """
    warnings: list[str] = []
    output_file = None

    try:
        output_file = open(filepath, "wb")
        exporter = KN5Exporter(output_file, context, warnings)
        exporter.write()

        return {"status": "success", "warnings": warnings}

    except Exception as e:
        error_trace = traceback.format_exc()
        warnings.append(f"Export failed: {e}")
        warnings.append(error_trace)

        # Remove broken file to prevent loading errors in AC
        try:
            Path(filepath).unlink(missing_ok=True)
        except OSError:
            pass

        return {"status": "error", "warnings": warnings}

    finally:
        if output_file:
            output_file.close()
