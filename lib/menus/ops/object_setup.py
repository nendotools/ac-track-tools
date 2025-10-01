"""Operators for setting up objects with AC-specific configurations."""

import bpy
from bpy.types import Operator
from mathutils import Vector

from ...kn5.shader_defaults import get_shader_defaults


class AC_SetupAsTree(Operator):
    """Setup selected meshes as trees with ksTree shader and correct naming"""

    bl_idname = "ac.setup_as_tree"
    bl_label = "Setup as Tree"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        count = self._get_next_tree_number(context)

        for obj in meshes:
            # Rename with KSTREE_GROUP_ prefix
            base_name = obj.name.replace("KSTREE_GROUP_", "").split("_")[0]
            obj.name = f"KSTREE_GROUP_{base_name}_{count}"
            count += 1

            # Set origin to bottom of mesh
            self._set_origin_to_bottom(context, obj)

            # Setup materials
            for slot in obj.material_slots:
                if slot.material:
                    self._setup_material(slot.material, "ksTree")

            # Set KN5 object properties
            obj.AC_KN5.cast_shadows = True
            obj.AC_KN5.transparent = False
            obj.AC_KN5.visible = True
            obj.AC_KN5.renderable = True

        self.report({'INFO'}, f"Configured {len(meshes)} object(s) as trees")
        return {'FINISHED'}

    def _get_next_tree_number(self, context) -> int:
        """Get next available tree number."""
        max_num = 0
        for obj in context.blend_data.objects:
            if obj.name.startswith("KSTREE_GROUP_"):
                parts = obj.name.split("_")
                if len(parts) >= 3 and parts[-1].isdigit():
                    max_num = max(max_num, int(parts[-1]))
        return max_num + 1

    def _set_origin_to_bottom(self, context, obj):
        """Move object origin to bottom of bounding box."""
        # Save cursor location
        cursor_loc = context.scene.cursor.location.copy()

        # Get world space bounding box
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        min_z = min(v.z for v in bbox)

        # Calculate center X, Y but use min Z
        center_x = sum(v.x for v in bbox) / 8
        center_y = sum(v.y for v in bbox) / 8

        # Set cursor to bottom center
        context.scene.cursor.location = (center_x, center_y, min_z)

        # Set origin to cursor
        old_active = context.view_layer.objects.active
        context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.view_layer.objects.active = old_active

        # Restore cursor
        context.scene.cursor.location = cursor_loc

    def _setup_material(self, material, shader_name: str):
        """Configure material with shader-specific settings."""
        ac_mat = material.AC_Material
        defaults = get_shader_defaults(shader_name)

        # Set shader settings
        ac_mat.shader_name = shader_name
        ac_mat.alpha_tested = defaults["alpha_tested"]
        ac_mat.alpha_blend_mode = str(defaults["alpha_blend_mode"])
        ac_mat.depth_mode = str(defaults["depth_mode"])

        # Clear and add shader properties
        ac_mat.shader_properties.clear()
        for prop_data in defaults["properties"]:
            prop = ac_mat.shader_properties.add()
            prop.name = prop_data["name"]
            prop.valueA = prop_data["valueA"]


class AC_SetupAsGrass(Operator):
    """Setup selected meshes as grass with ksGrass shader"""

    bl_idname = "ac.setup_as_grass"
    bl_label = "Setup as Grass"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        missing_variation = []

        for obj in meshes:
            # Setup materials
            for slot in obj.material_slots:
                if slot.material:
                    AC_SetupAsTree._setup_material(self, slot.material, "ksGrass")

                    # Check for variation texture
                    if not self._has_variation_texture(slot.material):
                        missing_variation.append(slot.material.name)

            # Set KN5 object properties
            obj.AC_KN5.cast_shadows = True
            obj.AC_KN5.transparent = False

        self.report({'INFO'}, f"Configured {len(meshes)} object(s) as grass")

        if missing_variation:
            mats = ", ".join(set(missing_variation))
            self.report({'WARNING'}, f"Materials need txVariation texture: {mats}")

        return {'FINISHED'}

    def _has_variation_texture(self, material) -> bool:
        """Check if material has a texture node with txVariation slot."""
        if not material.node_tree:
            return False

        for node in material.node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeTexImage):
                if hasattr(node, 'AC_Texture'):
                    if node.AC_Texture.shader_input_name == "txVariation":
                        return True
        return False


class AC_SetupAsStandard(Operator):
    """Setup selected meshes with ksPerPixel shader"""

    bl_idname = "ac.setup_as_standard"
    bl_label = "Setup as Standard Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        for obj in meshes:
            # Setup materials
            for slot in obj.material_slots:
                if slot.material:
                    AC_SetupAsTree._setup_material(self, slot.material, "ksPerPixel")

            # Set KN5 object properties
            obj.AC_KN5.cast_shadows = True
            obj.AC_KN5.transparent = False

        self.report({'INFO'}, f"Configured {len(meshes)} object(s) as standard")
        return {'FINISHED'}


class AC_AutoSetupObjects(Operator):
    """Automatically setup objects based on naming patterns"""

    bl_idname = "ac.auto_setup_objects"
    bl_label = "Auto Setup by Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Scan object names and auto-configure (tree/grass)"

    def execute(self, context):
        tree_count = 0
        grass_count = 0

        for obj in context.blend_data.objects:
            if obj.type != 'MESH' or obj.name.startswith("__"):
                continue

            name_lower = obj.name.lower()

            # Auto-detect trees
            if 'tree' in name_lower or obj.name.startswith("KSTREE_GROUP_"):
                context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.ac.setup_as_tree()
                obj.select_set(False)
                tree_count += 1

            # Auto-detect grass
            elif 'grass' in name_lower:
                context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.ac.setup_as_grass()
                obj.select_set(False)
                grass_count += 1

        self.report({'INFO'}, f"Auto-configured {tree_count} trees, {grass_count} grass")
        return {'FINISHED'}
