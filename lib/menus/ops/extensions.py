from bpy.props import IntProperty, StringProperty
from bpy.types import Operator


class AC_AddGlobalExtension(Operator):
    """Add a global extension to the project"""
    bl_idname = "ac.global_add_extension"
    bl_label = "Add Global Extension"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        ext_group = settings.global_extensions.add()
        ext_group.name = "_EXT"
        return {'FINISHED'}

class AC_RemoveGlobalExtension(Operator):
    """Remove a global extension from the project"""
    bl_idname = "ac.global_remove_extension"
    bl_label = "Remove Global Extension"
    bl_options = {'REGISTER'}
    name: StringProperty(
        name="Extension Name",
        default=""
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        if self.name == "":
            return {'CANCELLED'}
        for i, ext in enumerate(settings.global_extensions):
            if ext.name == self.name:
                settings.global_extensions.remove(i)
                break
        return {'FINISHED'}

class AC_ToggleGlobalExtension(Operator):
    """Toggle a global extension on or off"""
    bl_idname = "ac.global_toggle_extension"
    bl_label = "Toggle Global Extension"
    bl_options = {'REGISTER'}
    index: IntProperty(
        name="Extension Index",
        default=-1
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        ext_group = settings.global_extensions[self.index]
        if ext_group:
            ext_group.expand = not ext_group.expand
        return {'FINISHED'}

class AC_AddGlobalExtensionItem(Operator):
    """Add a new item to a global extension"""
    bl_idname = "ac.global_add_extension_item"
    bl_label = "Add Global Extension Item"
    bl_options = {'REGISTER'}
    name: StringProperty(
        name="Extension Name",
        default=""
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        ext_group = next((ext for ext in settings.global_extensions if ext.name == self.name), None)
        if ext_group:
            ext_group.items.add()
        return {'FINISHED'}

class AC_RemoveGlobalExtensionItem(Operator):
    """Remove an item from a global extension"""
    bl_idname = "ac.global_remove_extension_item"
    bl_label = "Remove Global Extension Item"
    bl_options = {'REGISTER'}
    ext_index: IntProperty(
        name="Extension Index",
        default=-1
    )
    item_index: IntProperty(
        name="Item Index",
        default=-1
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        ext_group = settings.global_extensions[self.ext_index]
        ext_group.items.remove(self.item_index)
        return {'FINISHED'}
