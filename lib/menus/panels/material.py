"""Material properties panel for Assetto Corsa KN5 export."""

from bpy.types import Operator, Panel, UIList


class AC_UL_ShaderProperties(UIList):
    """UI List for shader properties."""

    def draw_item(self, context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "name", text="", emboss=False)


class PROPERTIES_PT_AC_Material(Panel):
    """Material properties panel in Properties context."""

    bl_label = "Assetto Corsa"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout
        material = context.material
        ac_mat = material.AC_Material

        # Shader settings
        layout.prop(ac_mat, "shader_name")
        layout.prop(ac_mat, "alpha_blend_mode")
        layout.prop(ac_mat, "alpha_tested")
        layout.prop(ac_mat, "depth_mode")

        # Shader properties list
        box = layout.box()
        box.label(text="Shader Properties")

        if ac_mat.shader_properties:
            box.template_list(
                "AC_UL_ShaderProperties",
                "",
                ac_mat,
                "shader_properties",
                ac_mat,
                "shader_properties_active",
                rows=3
            )

            # Show active property editor
            if 0 <= ac_mat.shader_properties_active < len(ac_mat.shader_properties):
                active_prop = ac_mat.shader_properties[ac_mat.shader_properties_active]
                col = box.column(align=True)
                col.prop(active_prop, "name")
                col.separator()
                col.prop(active_prop, "valueA")
                col.prop(active_prop, "valueB")
                col.prop(active_prop, "valueC")
                col.prop(active_prop, "valueD")

        # Add/Remove buttons
        row = box.row()
        row.operator("ac.add_shader_property", icon='ADD')
        row.operator("ac.remove_shader_property", icon='REMOVE')


class AC_AddShaderProperty(Operator):
    """Add shader property to material"""

    bl_idname = "ac.add_shader_property"
    bl_label = "Add Shader Property"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ac_mat = context.material.AC_Material
        prop = ac_mat.shader_properties.add()
        prop.name = "ksProperty"
        ac_mat.shader_properties_active = len(ac_mat.shader_properties) - 1
        return {'FINISHED'}


class AC_RemoveShaderProperty(Operator):
    """Remove shader property from material"""

    bl_idname = "ac.remove_shader_property"
    bl_label = "Remove Shader Property"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ac_mat = context.material.AC_Material
        if 0 <= ac_mat.shader_properties_active < len(ac_mat.shader_properties):
            ac_mat.shader_properties.remove(ac_mat.shader_properties_active)
            ac_mat.shader_properties_active = max(0, ac_mat.shader_properties_active - 1)
        return {'FINISHED'}
