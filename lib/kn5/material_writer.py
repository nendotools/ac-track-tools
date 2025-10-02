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

    def get_material_id(self, material) -> int:
        """Get material ID, adding it if not already collected (for evaluated meshes)."""
        if material.name in self.material_positions:
            return self.material_positions[material.name]

        # Material not found - this can happen with evaluated meshes from modifiers
        # Add it now with validation
        position = len(self.material_positions)
        mat_props = MaterialProperties(material, self.warnings)
        self.available_materials[material.name] = mat_props
        self.material_positions[material.name] = position

        # Validate texture paths for dynamically added materials
        from ...utils.files import get_texture_directory
        texture_dir = get_texture_directory()

        texture_issues = []
        if material.node_tree:
            import bpy
            for node in material.node_tree.nodes:
                if isinstance(node, bpy.types.ShaderNodeTexImage) and node.image:
                    if not node.image.filepath:
                        texture_issues.append(f"texture '{node.image.name}' has no filepath")
                    elif not node.image.filepath.startswith("//"):
                        texture_issues.append(f"texture '{node.image.name}' uses absolute path (should be relative)")
                    else:
                        # Check if texture is in content/texture directory
                        abs_path = bpy.path.abspath(node.image.filepath)
                        if texture_dir not in abs_path:
                            texture_issues.append(f"texture '{node.image.name}' not in content/texture directory")

        warning_msg = f"Material '{material.name}' added from evaluated mesh (Geometry Nodes/modifiers)"
        if texture_issues:
            warning_msg += f" - Issues: {'; '.join(texture_issues)}"
        self.warnings.append(warning_msg)

        return position

    def write(self) -> None:
        """Write material count and all material definitions."""
        self.write_int(len(self.available_materials))
        for material_name, _position in sorted(self.material_positions.items(), key=lambda k: k[1]):
            material = self.available_materials[material_name]
            self._write_material(material)

    def _is_object_hidden(self, obj) -> bool:
        """Check if object is in any hidden collection."""
        for collection in obj.users_collection:
            if collection.hide_viewport:
                return True
        return False

    def _collect_object_materials(self, obj, materials: set) -> None:
        """Recursively collect materials from object and its children."""
        if obj.name.startswith("__"):
            return
        if self._is_object_hidden(obj):
            return

        # Collect materials from this object
        if hasattr(obj, 'material_slots'):
            for slot in obj.material_slots:
                if slot.material and not slot.material.name.startswith("__"):
                    materials.add(slot.material)

        # Recursively collect from children
        for child in obj.children:
            self._collect_object_materials(child, materials)

    def _collect_materials(self) -> None:
        """Collect all materials used by mesh objects in scene."""
        position = 0
        scene_materials = set()

        # Collect materials from all visible root objects and their children
        for obj in self.context.scene.objects:
            # Only process root objects (children will be handled recursively)
            if obj.parent:
                continue
            # Skip if object name starts with __
            if obj.name.startswith("__"):
                continue
            # Skip instancer objects (tree/grass scatter systems)
            if obj.name.startswith("KSTREE_GROUP_") or obj.name.startswith("GRASS_"):
                continue
            # Skip template/example objects
            name_lower = obj.name.lower()
            if "_profile" in name_lower or "_example" in name_lower or "collider" in name_lower:
                continue
            # Skip if object is in a hidden collection
            if self._is_object_hidden(obj):
                continue

            self._collect_object_materials(obj, scene_materials)

        for material in scene_materials:
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
