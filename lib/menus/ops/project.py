import math
import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from ....utils.files import ensure_path_exists, get_active_directory, get_data_directory, get_ui_directory, load_ini, load_json, save_ini, save_json


class AC_SaveSettings(Operator):
    """Save the current settings"""
    bl_idname = "ac.save_settings"
    bl_label = "Save Settings"
    bl_options = {'REGISTER'}
    def execute(self, context):
        print("Saving settings")
        settings = context.scene.AC_Settings # type: ignore
        data_dir = get_data_directory()
        surface_data = settings.map_surfaces()
        if 'surface' in list(settings.error.keys()):
            msg = settings.error['surface']
            settings.reset_errors()
            self.report({'ERROR'}, msg)
            return { 'CANCELLED' }
        save_ini(data_dir + '/surface.ini', surface_data)

        ui_dir = get_ui_directory()
        track_data = settings.map_track()
        save_json(ui_dir + '/ui_track.json', track_data)
        print("Settings saved")
        return {'FINISHED'}

class AC_LoadSettings(Operator):
    """Load the current settings"""
    bl_idname = "ac.load_settings"
    bl_label = "Load Settings"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        data_dir = get_data_directory()
        surface_map = load_ini(data_dir + '/surface.ini')
        if surface_map:
            settings.load_surfaces(surface_map)

        ui_dir = get_ui_directory()
        track = load_json(ui_dir + '/ui_track.json')
        if track:
            settings.load_track(track)

        return {'FINISHED'}

class AC_AddStart(Operator):
    """Add a new start position"""
    bl_idname = "ac.add_start"
    bl_label = "Add Start"
    bl_options = {'REGISTER'}
    def execute(self, context):
        # create empty SingleArrow object at mouse location
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        start_pos = bpy.context.object
        print("start_pos", start_pos)
        start_pos.name = "AC_START_0"
        return {'FINISHED'}

class AC_AddHotlapStart(Operator):
    """Add a new hotlap start position"""
    bl_idname = "ac.add_hotlap_start"
    bl_label = "Add Hotlap Start"
    bl_options = {'REGISTER'}
    def execute(self, context):
        # create empty SingleArrow object at mouse location
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        start_pos = bpy.context.object
        print("start_pos", start_pos)
        start_pos.name = "AC_HOTLAP_START_0"
        return {'FINISHED'}

class AC_AddPitbox(Operator):
    """Add a new pitbox"""
    bl_idname = "ac.add_pitbox"
    bl_label = "Add Pitbox"
    bl_options = {'REGISTER'}
    def execute(self, context):
        # create empty SingleArrow object at mouse location
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        pitbox = bpy.context.object
        print("pitbox", pitbox)
        pitbox.name = "AC_PIT_0"
        return {'FINISHED'}
