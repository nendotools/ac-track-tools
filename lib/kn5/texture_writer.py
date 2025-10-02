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
        self._clean_auto_exported_textures()
        self._collect_texture_nodes()

    def write(self) -> None:
        """Write texture count and all texture data."""
        self.write_int(len(self.available_textures))
        for texture_name, _position in sorted(self.texture_positions.items(), key=lambda k: k[1]):
            self._write_texture(self.available_textures[texture_name])

    def _clean_auto_exported_textures(self) -> None:
        """
        Clean up auto-exported textures from previous exports.
        Removes files matching the pattern: *_{8_hex_chars}.{ext}
        """
        import os
        import re
        from ...utils.files import get_texture_directory

        texture_dir = get_texture_directory()
        if not os.path.exists(texture_dir):
            return

        # Pattern matches: anything_{8 hex chars}.ext
        auto_export_pattern = re.compile(r'^.+_[0-9a-f]{8}\.(png|dds)$', re.IGNORECASE)

        cleaned_count = 0
        try:
            for filename in os.listdir(texture_dir):
                if auto_export_pattern.match(filename):
                    file_path = os.path.join(texture_dir, filename)
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except Exception as e:
                        self.warnings.append(f"Failed to remove old texture '{filename}': {e}")

            if cleaned_count > 0:
                self.warnings.append(f"Cleaned {cleaned_count} auto-exported texture(s) from previous export")
        except Exception as e:
            self.warnings.append(f"Failed to clean content/texture directory: {e}")

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
        for obj in self.context.scene.objects:
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

        # Get image data and export to content/texture directory
        image_data = self._get_image_data(texture_node)
        texture_filename = self._export_texture_to_content_dir(texture_node.image, image_data)

        # Write the actual filename to KN5 (not the Blender image name)
        self.write_string(texture_filename)
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

    def _export_texture_to_content_dir(self, image, image_data: bytes) -> str:
        """
        Export texture to content/texture directory.
        Does not modify scene - only writes file to disk.
        Uses deterministic naming for safe overwrites.

        Returns: The filename (not full path) written to content/texture.
        """
        import os
        import hashlib
        from ...utils.files import get_texture_directory

        texture_dir = get_texture_directory()
        if not os.path.exists(texture_dir):
            os.makedirs(texture_dir, exist_ok=True)

        # Determine file extension from image format or data
        file_ext = ".png"
        if image_data[:3] == DDS_HEADER_BYTES:
            file_ext = ".dds"
        elif image.file_format == "PNG":
            file_ext = ".png"
        elif image.file_format == "DDS":
            file_ext = ".dds"

        # Create deterministic filename based on image name and data hash
        # This ensures the same texture always produces the same filename
        base_name = os.path.splitext(image.name)[0]

        # Sanitize base name (remove invalid chars for filenames)
        base_name = "".join(c for c in base_name if c.isalnum() or c in ('-', '_'))

        # Add hash suffix to ensure uniqueness and repeatability
        data_hash = hashlib.md5(image_data).hexdigest()[:8]
        texture_filename = f"{base_name}_{data_hash}{file_ext}"
        texture_path = os.path.join(texture_dir, texture_filename)

        # Write texture file (safe to overwrite - same data produces same filename)
        try:
            file_exists = os.path.exists(texture_path)
            with open(texture_path, 'wb') as f:
                f.write(image_data)

            # Report export status
            size_kb = len(image_data) / 1024
            if file_exists:
                self.warnings.append(f"Updated texture in content/texture: '{texture_filename}' ({size_kb:.1f} KB)")
            else:
                self.warnings.append(f"Exported texture to content/texture: '{texture_filename}' ({size_kb:.1f} KB)")
        except Exception as e:
            self.warnings.append(f"Failed to export texture '{image.name}' to content/texture: {e}")

        return texture_filename
