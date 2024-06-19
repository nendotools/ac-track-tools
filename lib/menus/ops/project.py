import math

import bpy
from bpy.types import Operator
from os import path

from ....utils.files import (get_data_directory, get_extension_directory,
                             get_ui_directory, load_ini, load_json, save_ini,
                             save_json)
from ...settings import AC_Settings


class AC_SaveSettings(Operator):
    """Save the current settings"""
    bl_idname = "ac.save_settings"
    bl_label = "Save Settings"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore

        ui_dir = get_ui_directory()
        track_data = settings.map_track(context)
        save_json(ui_dir + '/ui_track.json', track_data)

        data_dir = get_data_directory()
        surface_data = settings.map_surfaces()
        if 'surface' in list(settings.surface_errors.keys()):
            msg = settings.surface_errors['surface']
            settings.reset_errors()
            self.report({'ERROR'}, msg)
            return { 'CANCELLED' }
        save_ini(data_dir + '/surfaces.ini', surface_data)

        audio_data = settings.map_audio()
        save_ini(data_dir + '/audio_sources.ini', audio_data)

        save_ini(data_dir + '/lighting.ini', settings.map_lighting())

        extension_map: dict = settings.map_extensions()
        if 'extension' not in list(settings.surface_errors.keys()) and len(extension_map.keys()) > 0:
            extension_dir = get_extension_directory()
            save_ini(extension_dir + '/ext_config.ini', extension_map)
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

        lighting_map = load_ini(data_dir + '/lighting.ini')
        if lighting_map:
            settings.load_lighting(lighting_map)

        extension_dir = get_extension_directory()
        extension_map = load_ini(extension_dir + '/ext_config.ini')
        if extension_map:
            settings.load_extensions(extension_map)
        return {'FINISHED'}

class AC_ExportTrack(Operator):
    """Export track as FBX"""
    bl_idname = "ac.export_track"
    bl_label = "Export Track"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        target = settings.working_dir.rstrip(path.sep).split(path.sep)[-1]
        bpy.ops.export_scene.fbx(
            filepath=settings.working_dir + target + '.fbx',
            object_types={'EMPTY','MESH'},
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_UNITS',
            use_space_transform=True,
            use_mesh_modifiers=True,
            axis_up='Y',
            axis_forward='-Z',
        )
        return {'FINISHED'}

class AC_AutofixPreflight(Operator):
    """Attempt to fix common issues"""
    bl_idname = "ac.autofix_preflight"
    bl_label = "Autofix Preflight"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.track.pitboxes = len(settings.get_pitboxes(context))
        settings.consolidate_logic_gates(context)
        context.scene.unit_settings.system = 'METRIC'
        context.scene.unit_settings.length_unit = 'METERS'
        context.scene.unit_settings.scale_length = 1
        return {'FINISHED'}

class AC_AddStart(Operator):
    """Add a new start position"""
    bl_idname = "ac.add_start"
    bl_label = "Add Start"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, math.pi, 0))
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        start_pos = bpy.context.object
        # get next start position
        start_pos.name = f"AC_START_{len(settings.get_starts(context))}"
        return {'FINISHED'}

class AC_AddHotlapStart(Operator):
    """Add a new hotlap start position"""
    bl_idname = "ac.add_hotlap_start"
    bl_label = "Add Hotlap Start"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, math.pi, 0))
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        start_pos = bpy.context.object
        start_pos.name = f"AC_HOTLAP_START_{len(settings.get_hotlap_starts(context))}"
        return {'FINISHED'}

class AC_AddPitbox(Operator):
    """Add a new pitbox"""
    bl_idname = "ac.add_pitbox"
    bl_label = "Add Pitbox"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, math.pi, 0))
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        pitbox = bpy.context.object
        pitbox.name = f"AC_PIT_{len(settings.get_pitboxes(context))}"
        return {'FINISHED'}

class AC_AddTimeGate(Operator):
    """Add a new time gate"""
    bl_idname = "ac.add_time_gate"
    bl_label = "Add Time Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        count = len(settings.get_time_gates(context)) // 2
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        time_gate_L = bpy.context.object
        time_gate_L.name = f"AC_TIME_{count}_L"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        time_gate_R = bpy.context.object
        time_gate_R.name = f"AC_TIME_{count}_R"
        return {'FINISHED'}

class AC_AddABStartGate(Operator):
    """Add a new AB start gate"""
    bl_idname = "ac.add_ab_start_gate"
    bl_label = "Add AB Start Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        ab_start_L = bpy.context.object
        ab_start_L.name = "AC_AB_START_L"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        ab_start_R = bpy.context.object
        ab_start_R.name = "AC_AB_START_R"
        return {'FINISHED'}

class AC_AddABFinishGate(Operator):
    """Add a new AB finish gate"""
    bl_idname = "ac.add_ab_finish_gate"
    bl_label = "Add AB Finish Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        ab_finish_L = bpy.context.object
        ab_finish_L.name = "AC_AB_FINISH_L"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        ab_finish_R = bpy.context.object
        ab_finish_R.name = "AC_AB_FINISH_R"
        return {'FINISHED'}

class AC_AddAudioEmitter(Operator):
    """Add a new audio emitter"""
    bl_idname = "ac.add_audio_emitter"
    bl_label = "Add Audio Emitter"
    bl_options = {'REGISTER'}
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        bpy.ops.object.empty_add(type='SPHERE', scale=(2, 2, 2))
        audio_emitter = bpy.context.object
        audio_emitter.name = f"AC_AUDIO_{len(settings.get_audio_emitters(context)) + 1}"
        return {'FINISHED'}
