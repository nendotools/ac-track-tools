import re
import bpy
from bpy.types import Object, Operator
from bpy.props import StringProperty

from ....utils.constants import SURFACE_REGEX
from ...configs.surface import AC_Surface
from ...settings import AC_Settings

class AC_InitSurfaces(Operator):
    bl_label = "Init Surfaces"
    bl_idname = "ac.init_surfaces"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.load_surfaces({})
        return {'FINISHED'}

class AC_AddSurface(Operator):
    bl_label = "Add Surface"
    bl_idname = "ac.add_surface"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        surface = settings.surfaces.add()
        # set surface name to unique
        surface.name = self.find_unique_name("Surface", settings)
        return {'FINISHED'}

    def find_unique_name(self, name: str, settings: AC_Settings):
        names = [surface.name for surface in settings.surfaces]
        if name not in names:
            return name
        i = 1
        while f"{name}.{i}" in names:
            i += 1
        return f"{name}.{i}"

class AC_RemoveSurface(Operator):
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

def remove_existing_prefix(name: str) -> str:
    match = re.match(SURFACE_REGEX, name)
    # check ignores empty groups and returns the last group
    # if the first group is not empty, assume there's no surface prefix
    if match and match.group(1) != '':
        if match.group(3):
            return match.group(3)
        return ''
    return name
