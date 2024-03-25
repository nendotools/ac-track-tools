import re

import bpy
from bpy.props import IntProperty, StringProperty
from bpy.types import Object, Operator

from ....utils.constants import SURFACE_REGEX
from ...configs.surface import AC_Surface
from ...settings import AC_Settings


class AC_InitSurfaces(Operator):
    """Initialize default surfaces"""
    bl_label = "Init Surfaces"
    bl_idname = "ac.init_surfaces"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.load_surfaces({})
        return {'FINISHED'}

class AC_AddSurface(Operator):
    """Add a new surface"""
    bl_label = "Add/Copy Surface"
    bl_idname = "ac.add_surface"
    bl_options = {'REGISTER'}
    copy_from: StringProperty(
        name="Copy Surface Key",
        default="",
    )

    @classmethod
    def description(cls, context, properties):
        if properties.copy_from != "":
            return f"Create a new surface based on {properties.copy_from}"
        return "Create a new surface"

    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        surface = settings.surfaces.add()
        surface.key = "SURFACE"
        if self.copy_from != "":
            source = next((s for s in settings.surfaces if s.key == self.copy_from), None)
            if source:
                for attr in source.keys():
                    setattr(surface, attr, getattr(source, attr))
                # update surface name to replace _ with space and title case
                surface.name = surface.key.replace("_", " ").title()
                surface.custom = True
        surface.key = self.find_unique_value(surface.key, "key", settings)
        surface.name = surface.key
        return {'FINISHED'}

    def find_unique_value(self, key: str, field: str, settings: AC_Settings):
        keys = []
        for surface in settings.surfaces:
            keys.append(getattr(surface, field))
        if key not in keys:
            return key
        i = 1
        num_check = re.match(r"^(.*?)([._-]?\d*)$", key)
        true_name = num_check.group(1) if num_check else key
        while f"{true_name}-{i}" in keys:
            i += 1
        return f"{true_name}-{i}"

class AC_RemoveSurface(Operator):
    """Remove a surface"""
    bl_label = "Remove Surface"
    bl_idname = "ac.remove_surface"
    bl_options = {'REGISTER'}

    target: StringProperty(
        name="Target",
        default="",
    )

    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        if self.target in settings.active_surfaces:
            settings.active_surfaces.remove(self.target)

        surface: AC_Surface
        for i, surface in enumerate(settings.surfaces):
            if surface.name == self.target:
                settings.surfaces.remove(i)
                break
        return {'FINISHED'}

class AC_ToggleSurface(Operator):
    """Toggle surface menu visibility"""
    bl_label = "Toggle Surface"
    bl_idname = "ac.toggle_surface"
    bl_options = {'REGISTER'}
    target: StringProperty(
        name="Target",
        default="",
    )
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        if self.target in settings.active_surfaces:
            settings.active_surfaces.remove(self.target)
        else:
            settings.active_surfaces.append(self.target)
        return {'FINISHED'}

class AC_AssignSurface(Operator):
    """Assign a surface type to selected objects"""
    bl_label = "Assign Surface"
    bl_idname = "ac.assign_surface"
    bl_options = {'REGISTER', 'UNDO'}
    key: StringProperty(
        name="Key",
        default="ROAD",
    )
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objects:
            cleaned_name = remove_existing_prefix(obj.name)
            obj.name = f"1{self.key}_{cleaned_name}"
        return {'FINISHED'}

class AC_SelectAllSurfaces(Operator):
    """Select all objects with the specified surface key"""
    bl_label = "Select All Surfaces"
    bl_idname = "ac.select_all_surfaces"
    bl_options = {'REGISTER', 'UNDO'}
    surface: StringProperty(
        name="Surface Key",
        default="",
    )
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        bpy.ops.object.select_all(action='DESELECT')
        for obj in settings.get_surface_groups(context, self.surface):
            if isinstance(obj, Object):
                obj.select_set(True)
        return {'FINISHED'}

class AC_AssignWall(Operator):
    """Assign a wall type to selected objects"""
    bl_label = "Convert to Wall"
    bl_idname = "ac.assign_wall"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings
        objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objects:
            verts = len(obj.data.vertices) # type: ignore
            if verts > 30:
                self.report({'WARNING'}, f"Object {obj.name} may be too complex to use as a wall. Consider using a more simple mesh.")
            cleaned_name = remove_existing_prefix(obj.name)
            obj.name = f"1WALL_{cleaned_name}"
        return {'FINISHED'}

class AC_AssignPhysProp(Operator):
    """Assign physical properties to selected objects"""
    bl_label = "Assign Physical Properties"
    bl_idname = "ac.assign_phys_prop"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings
        objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objects:
            cleaned_name = remove_existing_prefix(obj.name)
            obj.name = f"AC_POBJECT_{cleaned_name}"
        return {'FINISHED'}

class AC_AddSurfaceExt(Operator):
    """Add a new surface extension"""
    bl_label = "Add Surface Extension"
    bl_idname = "ac.add_surface_ext"
    bl_options = {'REGISTER', 'UNDO'}
    extension: StringProperty(
        name="Extension",
        default="",
    )
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings
        # if self.extension == "": add new extension
        # else: add properties to existing extension
        if self.extension == "":
            extension = settings.surface_ext.add()
        else:
            extension = next((ext for ext in settings.surface_ext if ext.name == self.extension), None)
            if not extension:
                extension = settings.surface_ext.add()
            extension.items.add()
        return {'FINISHED'}

class AC_DeleteSurfaceExt(Operator):
    """Delete a surface extension"""
    bl_label = "Delete Surface Extension"
    bl_idname = "ac.delete_surface_ext"
    bl_options = {'REGISTER', 'UNDO'}
    extension: StringProperty(
        name="Extension",
        default="",
    )
    index: IntProperty(
        name="Index",
        default=-1,
    )
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings
        # if extension is empty, delete the extension at the index
        # else: delete the property from the extension
        if self.extension == "":
            settings.surface_ext.remove(self.index)
        else:
            extension = next((ext for ext in settings.surface_ext if ext.name == self.extension), None)
            if extension:
                extension.items.remove(self.index)
        return {'FINISHED'}

def remove_existing_prefix(name: str) -> str:
    match = re.match(SURFACE_REGEX, name)
    # check ignores empty groups and returns the last group
    # if the first group is not empty, assume there's no surface prefix
    if match and match.group(1) != '':
        if match.group(3):
            return match.group(3)
        return ''
    return name
