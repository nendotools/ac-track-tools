from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

from .kn5_writer import KN5Writer

if TYPE_CHECKING:
    from bpy.types import Context, ShaderNodeTexImage

DDS_HEADER_BYTES = b"DDS"


class TextureWriter(KN5Writer):
    """Writes texture data to KN5 file."""

    def __init__(self, file, context: Context, warnings: list[str]):
        super().__init__(file)
        self.context = context
        self.warnings = warnings
        self.available_textures: dict[str, ShaderNodeTexImage] = {}
        self.texture_positions: dict[str, int] = {}
        self._collect_texture_nodes()

    def write(self) -> None:
        """Write texture count and all texture data."""
        self.write_int(len(self.available_textures))
        for texture_name, _position in sorted(self.texture_positions.items(), key=lambda k: k[1]):
            self._write_texture(self.available_textures[texture_name])

    def _collect_texture_nodes(self) -> None:
        """Collect all ShaderNodeTexImage nodes from scene materials."""
        position = 0
        texture_nodes = self._get_all_texture_nodes()

        for texture_node in texture_nodes:
            if texture_node.name.startswith("__"):
                continue

            if not texture_node.image:
                self.warnings.append(f"Ignoring texture node without image: '{texture_node.name}'")
                continue

            if not texture_node.image.pixels:
                self.warnings.append(f"Ignoring texture node without image data: '{texture_node.name}'")
                continue

            image_name = texture_node.image.name
            if image_name not in self.available_textures:
                self.available_textures[image_name] = texture_node
                self.texture_positions[image_name] = position
                position += 1

    def _get_all_texture_nodes(self) -> list[ShaderNodeTexImage]:
        """Get all ShaderNodeTexImage nodes from all mesh materials in scene."""
        texture_nodes = []
        for obj in self.context.blend_data.objects:
            if obj.type != "MESH":
                continue
            for slot in obj.material_slots:
                if slot.material and slot.material.node_tree:
                    for node in slot.material.node_tree.nodes:
                        if isinstance(node, bpy.types.ShaderNodeTexImage):
                            texture_nodes.append(node)
        return texture_nodes

    def _write_texture(self, texture_node: ShaderNodeTexImage) -> None:
        """Write single texture: active flag, name, and image data blob."""
        is_active = 1
        self.write_int(is_active)
        self.write_string(texture_node.image.name)
        image_data = self._get_image_data(texture_node)
        self.write_blob(image_data)

    def _get_image_data(self, texture_node: ShaderNodeTexImage) -> bytes:
        """
        Get image data as bytes, converting to PNG if necessary.

        Creates temporary copy to avoid modifying original image.
        """
        image_copy = texture_node.image.copy()
        try:
            if image_copy.file_format in ("PNG", "DDS", ""):
                if not image_copy.packed_file:
                    image_copy.pack()
                image_data = image_copy.packed_file.data
                image_header = image_data[:3]

                if image_copy.file_format != "" or image_header == DDS_HEADER_BYTES:
                    return image_data

            return self._convert_to_png(image_copy)
        finally:
            self.context.blend_data.images.remove(image_copy)

    def _convert_to_png(self, image) -> bytes:
        """Convert image to PNG format and return packed data."""
        if not image.packed_file:
            image.unpack(method="WRITE_LOCAL")
        image.file_format = "PNG"
        image.pack()
        return image.packed_file.data
