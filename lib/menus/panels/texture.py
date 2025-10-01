"""Texture node panel for Assetto Corsa KN5 export."""

import bpy
from bpy.types import Panel


class NODE_PT_AC_Texture(Panel):
    """Texture node panel in Node Editor."""

    bl_label = "Assetto Corsa"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Assetto Corsa"

    @classmethod
    def poll(cls, context):
        if len(context.selected_nodes) == 1:
            return isinstance(context.selected_nodes[0], bpy.types.ShaderNodeTexImage)
        return False

    def draw(self, context):
        layout = self.layout
        node = context.selected_nodes[0]
        ac_texture = node.AC_Texture

        layout.prop(ac_texture, "shader_input_name")

        # Show hint about common texture slots
        box = layout.box()
        box.label(text="Common Slots:", icon='INFO')
        box.label(text="• txDiffuse (Base Color)")
        box.label(text="• txNormal (Normal Map)")
        box.label(text="• txDetail (Detail/Specular)")
        box.label(text="• txVariation (Grass variation)")
