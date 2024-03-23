import math
import bpy
from mathutils import Matrix, Vector
from bpy_extras import view3d_utils
from bpy.types import Depsgraph, Operator

from ....utils.files import (
    get_data_directory,
    get_ui_directory,
    get_extension_directory,
    load_ini,
    save_ini,
    load_json,
    save_json
)

class AC_SaveSettings(Operator):
    """Save the current settings"""
    bl_idname = "ac.save_settings"
    bl_label = "Save Settings"
    bl_options = {'REGISTER'}
    def execute(self, context):
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

        save_ini(data_dir + '/lighting.ini', settings.map_lighting())

        extension_map: dict = settings.map_extensions()
        if 'extension' not in list(settings.error.keys()) and len(extension_map.keys()) > 0:
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

class AC_AddStart(Operator):
    """Add a new start position"""
    bl_idname = "ac.add_start"
    bl_label = "Add Start"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        start_pos = bpy.context.object
        start_pos.name = "AC_START_0"
        return {'FINISHED'}

class AC_AddHotlapStart(Operator):
    """Add a new hotlap start position"""
    bl_idname = "ac.add_hotlap_start"
    bl_label = "Add Hotlap Start"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        start_pos = bpy.context.object
        start_pos.name = "AC_HOTLAP_START_0"
        return {'FINISHED'}

class AC_AddPitbox(Operator):
    """Add a new pitbox"""
    bl_idname = "ac.add_pitbox"
    bl_label = "Add Pitbox"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(math.pi * -0.5, 0, 0))
        pitbox = bpy.context.object
        pitbox.name = "AC_PIT_0"
        return {'FINISHED'}

class AC_AddTimeGate(Operator):
    """Add a new time gate"""
    bl_idname = "ac.add_time_gate"
    bl_label = "Add Time Gate"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0))
        time_gate_L = bpy.context.object
        time_gate_L.name = "AC_TIME_0_L"
        bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0))
        time_gate_R = bpy.context.object
        time_gate_R.name = "AC_TIME_0_R"
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

class AC_AddABStartGateModal(Operator):
    """Add a new AB start gate"""
    bl_idname = "ac.add_ab_start_gate_modal"
    bl_label = "Add AB Start Gate by Modal"
    bl_options = {'REGISTER'}

    # Modal Operator to place the AB Start Gate with the mouse
    # should detect the ground and place the gate there
    # should have a cancel option using ESC
    # should have a confirm option using LMB
    # should increase distance between L and R gates with Shift + mouse wheel
    # should rotate the gate with CTRL + mouse wheel
    # should have a preview of the gate while placing it
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            print(f"Mouse move at {event.mouse_x}, {event.mouse_y}")
            return {'RUNNING_MODAL'}
        elif event.type == 'LEFTMOUSE':
            print(f"Left mouse at {event.mouse_x}, {event.mouse_y}")
            position = self.mouse_to_xy(context, event)
            print(f"Left mouse at {position}")
            # place the gate at the position on the xy plane with 20 units between L and R gates
            bpy.ops.object.delete()
            bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(position[0] - 10, position[1], 0))
            ab_start_L = bpy.context.object
            ab_start_L.name = "AC_AB_START_L"
            bpy.ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(position[0] + 10, position[1], 0))
            ab_start_R = bpy.context.object
            ab_start_R.name = "AC_AB_START_R"
            # delete the empty circle
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("Right mouse or ESC")
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.execute(context)

    def execute(self, context):
        # create an empty circle flat on the xy plane
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

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
        bpy.ops.object.empty_add(type='SPHERE', scale=(2, 2, 2))
        audio_emitter = bpy.context.object
        audio_emitter.name = f"AC_AUDIO_1"
        return {'FINISHED'}
