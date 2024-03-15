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

        ui_dir = get_ui_directory()
        track_data = settings.map_track()
        save_json(ui_dir + '/ui_track.json', track_data)

        data_dir = get_data_directory()
        surface_data = settings.map_surfaces()
        if 'surface' in list(settings.error.keys()):
            msg = settings.error['surface']
            settings.reset_errors()
            self.report({'ERROR'}, msg)
            return { 'CANCELLED' }
        save_ini(data_dir + '/surfaces.ini', surface_data)

        audio_data = settings.map_audio()
        save_ini(data_dir + '/audio_sources.ini', audio_data)
        print("Settings saved")
        return {'FINISHED'}

class AC_LoadSettings(Operator):
    """Load the current settings"""
    bl_idname = "ac.load_settings"
    bl_label = "Load Settings"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore

        ui_dir = get_ui_directory()
        track = load_json(ui_dir + '/ui_track.json')
        if track:
            settings.load_track(track)

        data_dir = get_data_directory()
        surface_map = load_ini(data_dir + '/surfaces.ini')
        if surface_map:
            settings.load_surfaces(surface_map)

        audio_map = load_ini(data_dir + '/audio_sources.ini')
        if audio_map:
            settings.load_audio(audio_map)

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
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0))
        pitbox = bpy.context.object
        print("pitbox", pitbox)
        pitbox.name = "AC_PIT_0"
        return {'FINISHED'}

class AC_AddTimeGate(Operator):
    """Add a new time gate"""
    bl_idname = "ac.add_time_gate"
    bl_label = "Add Time Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(10, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        direction_indicator = bpy.context.object
        direction_indicator.name = "TIMEGATE_0"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        time_gate_L = bpy.context.object
        time_gate_L.name = "AC_TIME_0_L"
        bpy.context.view_layer.objects.active = direction_indicator
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        time_gate_R = bpy.context.object
        time_gate_R.name = "AC_TIME_0_R"
        bpy.context.view_layer.objects.active = direction_indicator
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        return {'FINISHED'}

class AC_AddABStartGate(Operator):
    """Add a new AB start gate"""
    bl_idname = "ac.add_ab_start_gate"
    bl_label = "Add AB Start Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(10, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        direction_indicator = bpy.context.object
        direction_indicator.name = "AB_START"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        ab_start_L = bpy.context.object
        ab_start_L.name = "AC_AB_START_L"
        bpy.context.view_layer.objects.active = direction_indicator
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        ab_start_R = bpy.context.object
        ab_start_R.name = "AC_AB_START_R"
        bpy.context.view_layer.objects.active = direction_indicator
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        return {'FINISHED'}

class AC_AddABFinishGate(Operator):
    """Add a new AB finish gate"""
    bl_idname = "ac.add_ab_finish_gate"
    bl_label = "Add AB Finish Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(10, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        direction_indicator = bpy.context.object
        direction_indicator.name = "AB_FINISH"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        ab_finish_L = bpy.context.object
        ab_finish_L.name = "AC_AB_FINISH_L"
        bpy.context.view_layer.objects.active = direction_indicator
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        ab_finish_R = bpy.context.object
        ab_finish_R.name = "AC_AB_FINISH_R"
        bpy.context.view_layer.objects.active = direction_indicator
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        return {'FINISHED'}

class AC_AddAudioEmitter(Operator):
    """Add a new audio emitter"""
    bl_idname = "ac.add_audio_emitter"
    bl_label = "Add Audio Emitter"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SPHERE', scale=(2, 2, 2))
        audio_emitter = bpy.context.object
        audio_emitter.name = f"AC_AUDIO_1"
        return {'FINISHED'}
