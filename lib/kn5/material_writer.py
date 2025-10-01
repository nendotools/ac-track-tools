from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

from .kn5_writer import KN5Writer

if TYPE_CHECKING:
    from bpy.types import Context, Material, ShaderNodeTexImage


class ShaderProperty:
    """Represents an AC shader property with up to 4 component values."""

    def __init__(self, name: str):
        self.name = name
        self.value_a: float = 0.0
        self.value_b: tuple[float, float] = (0.0, 0.0)
        self.value_c: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.value_d: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)


class MaterialProperties:
    """Material data for KN5 export."""

    def __init__(self, material: Material, warnings: list[str]):
        self.name = material.name
        ac_mat = material.AC_Material

        # Read from PropertyGroup
        self.shader_name = ac_mat.shader_name
        self.alpha_blend_mode = int(ac_mat.alpha_blend_mode)
        self.alpha_tested = ac_mat.alpha_tested
        self.depth_mode = int(ac_mat.depth_mode)
        self.shader_properties = self._copy_shader_properties(material)
        self.texture_mapping = self._generate_texture_mapping(material, warnings)

    def _copy_shader_properties(self, material: Material) -> dict[str, ShaderProperty]:
        """Copy shader properties from material PropertyGroup."""
        ac_mat = material.AC_Material
        properties = {}

        for shader_prop in ac_mat.shader_properties:
            prop = ShaderProperty(shader_prop.name)
            prop.value_a = shader_prop.valueA
            prop.value_b = tuple(shader_prop.valueB)
            prop.value_c = tuple(shader_prop.valueC)
            prop.value_d = tuple(shader_prop.valueD)
            properties[shader_prop.name] = prop

        # Add default properties if empty (backward compatibility)
        if not properties and self.shader_name == "ksPerPixel":
            diffuse = ShaderProperty("ksDiffuse")
            diffuse.value_a = 0.4
            properties["ksDiffuse"] = diffuse

            ambient = ShaderProperty("ksAmbient")
            ambient.value_a = 0.4
            properties["ksAmbient"] = ambient

        return properties

    def _generate_texture_mapping(self, material: Material, warnings: list[str]) -> dict[str, str]:
        """
        Generate texture mapping from node tree.

        Priority:
        1. Use AC_Texture.shader_input_name if set
        2. Auto-detect from node connections
        3. Default to txDiffuse
        """
        mapping = {}

        if not material.node_tree:
            return mapping

        for node in material.node_tree.nodes:
            if not isinstance(node, bpy.types.ShaderNodeTexImage):
                continue

            if not node.image or node.image.name.startswith("__"):
                continue

            # Check if user manually set texture slot via PropertyGroup
            if hasattr(node, 'AC_Texture') and node.AC_Texture.shader_input_name:
                slot_name = node.AC_Texture.shader_input_name
                mapping[slot_name] = node.image.name
            else:
                # Auto-detect texture slot based on connected socket
                slot_name = self._detect_texture_slot(node, material)
                if slot_name:
                    mapping[slot_name] = node.image.name
                else:
                    # Default to diffuse if connection unclear
                    mapping["txDiffuse"] = node.image.name
                    warnings.append(
                        f"Material '{material.name}': Auto-assigned texture '{node.image.name}' to txDiffuse slot"
                    )

        return mapping

    def _detect_texture_slot(self, texture_node: ShaderNodeTexImage, material: Material) -> str | None:
        """Detect AC texture slot based on node connections."""
        if not material.node_tree:
            return None

        for link in material.node_tree.links:
            if link.from_node != texture_node:
                continue

            # Check what the texture is connected to
            to_socket_name = link.to_socket.name.lower()

            if "base color" in to_socket_name or "diffuse" in to_socket_name:
                return "txDiffuse"
            elif "normal" in to_socket_name:
                return "txNormal"
            elif "roughness" in to_socket_name or "specular" in to_socket_name:
                return "txDetail"

        return None


class MaterialWriter(KN5Writer):
    """Writes material definitions to KN5 file."""

    def __init__(self, file, context: Context, warnings: list[str]):
        super().__init__(file)
        self.context = context
        self.warnings = warnings
        self.available_materials: dict[str, MaterialProperties] = {}
        self.material_positions: dict[str, int] = {}
        self._collect_materials()

    def write(self) -> None:
        """Write material count and all material definitions."""
        self.write_int(len(self.available_materials))
        for material_name, _position in sorted(self.material_positions.items(), key=lambda k: k[1]):
            material = self.available_materials[material_name]
            self._write_material(material)

    def _collect_materials(self) -> None:
        """Collect all materials used by mesh objects in scene."""
        position = 0

        for material in self.context.blend_data.materials:
            if material.users == 0:
                self.warnings.append(f"Ignoring unused material: '{material.name}'")
                continue

            if material.name.startswith("__"):
                continue

            mat_props = MaterialProperties(material, self.warnings)
            self.available_materials[material.name] = mat_props
            self.material_positions[material.name] = position
            position += 1

    def _write_material(self, material: MaterialProperties) -> None:
        """Write single material definition."""
        self.write_string(material.name)
        self.write_string(material.shader_name)
        self.write_byte(material.alpha_blend_mode)
        self.write_bool(material.alpha_tested)
        self.write_int(material.depth_mode)

        # Write shader properties
        self.write_uint(len(material.shader_properties))
        for prop_name in material.shader_properties:
            self._write_shader_property(material.shader_properties[prop_name])

        # Write texture mappings
        self.write_uint(len(material.texture_mapping))
        texture_slot = 0
        for slot_name in material.texture_mapping:
            self.write_string(slot_name)
            self.write_uint(texture_slot)
            self.write_string(material.texture_mapping[slot_name])
            texture_slot += 1

    def _write_shader_property(self, prop: ShaderProperty) -> None:
        """Write shader property with all 4 value components."""
        self.write_string(prop.name)
        self.write_float(prop.value_a)
        self.write_vector2(prop.value_b)
        self.write_vector3(prop.value_c)
        self.write_vector4(prop.value_d)
