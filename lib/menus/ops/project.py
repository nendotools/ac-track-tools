import math
from os import path

from bpy import ops
from bpy.types import Context, Operator

from ....utils.files import (get_data_directory, get_extension_directory,
                             get_texture_directory, get_ui_directory, load_ini,
                             load_json, save_ini, save_json)
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

        get_texture_directory() # only need to ensure the directory exists
        # TODO: check materials for texture paths and update them to use the texture directory + relocate the textures

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

        # Ensure default layout and base_track collection exist before saving
        settings.layout_settings.ensure_default_layout()

        layouts_data = settings.map_layouts()
        if layouts_data and layouts_data.get("layouts"):
            save_json(ui_dir + '/layouts.json', layouts_data)

            # Generate models.ini (or models_[layout].ini) files for each layout
            from ....utils.files import get_active_directory
            working_dir = get_active_directory()
            if working_dir:
                generated_files = settings.layout_settings.export_models_ini(working_dir)
                if generated_files:
                    print(f"Generated {len(generated_files)} models INI file(s)")

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

        get_texture_directory() # only need to ensure the directory exists

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

        layouts_data = load_json(ui_dir + '/layouts.json')
        if layouts_data:
            settings.load_layouts(layouts_data)

        # Ensure default layout and base_track collection exist after loading
        settings.layout_settings.ensure_default_layout()

        return {'FINISHED'}

class AC_ExportTrack(Operator):
    """Export track in selected format(s)"""
    bl_idname = "ac.export_track"
    bl_label = "Export Track"
    bl_options = {'REGISTER'}
    def execute(self, context):
        ops.ac.save_settings()
        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        exp_opts = settings.export_settings
        track_name = settings.working_dir.rstrip(path.sep).split(path.sep)[-1]

        # Get exportable collections
        collections = self._get_exportable_collections(context)

        if not collections:
            self.report({'ERROR'}, "No exportable collections found")
            return {'CANCELLED'}

        export_count = 0
        failed_exports = []

        for collection in collections:
            # Determine filename
            # Use track name for single collection or for "default" collection
            if len(collections) == 1 or collection.name == "default":
                filename = track_name
            else:
                filename = collection.name

            # Temporarily hide other collections
            original_visibility = self._hide_other_collections(context, collection)

            try:
                if exp_opts.use_kn5:
                    success = self._export_kn5(context, settings, filename, collection)
                else:
                    success = self._export_fbx(context, settings, exp_opts, filename)

                if success:
                    export_count += 1
                else:
                    failed_exports.append(filename)

            finally:
                # Restore collection visibility
                self._restore_collection_visibility(original_visibility)

        # Report results
        if failed_exports:
            msg = f"Exported {export_count}/{len(collections)}. Failed: {', '.join(failed_exports)}"
            self.report({'WARNING'}, msg)
        else:
            self.report({'INFO'}, f"Successfully exported {export_count} file(s)")

        return {'FINISHED'}

    def _get_exportable_collections(self, context) -> list:
        """Get non-hidden, non-excluded collections with objects."""
        collections = []
        for collection in context.blend_data.collections:
            # Skip if collection is hidden or excluded
            if collection.hide_viewport or collection.hide_render:
                continue
            # Skip if collection name starts with __
            if collection.name.startswith("__"):
                continue
            # Skip if collection has no objects
            if not collection.objects:
                continue
            collections.append(collection)
        return collections

    def _hide_other_collections(self, context, active_collection) -> dict:
        """Hide all collections except the active one. Returns original visibility state."""
        original_visibility = {}
        for collection in context.blend_data.collections:
            original_visibility[collection.name] = collection.hide_viewport
            if collection != active_collection:
                collection.hide_viewport = True
        return original_visibility

    def _restore_collection_visibility(self, original_visibility: dict):
        """Restore collection visibility to original state."""
        import bpy
        for collection_name, was_hidden in original_visibility.items():
            if collection_name in bpy.data.collections:
                bpy.data.collections[collection_name].hide_viewport = was_hidden

    def _export_kn5(self, context, settings, filename: str, collection) -> bool:
        """Export single collection to KN5."""
        try:
            from ...kn5 import export_kn5
        except ImportError as e:
            self.report({'ERROR'}, f"KN5 export module not available: {e}")
            return False

        filepath = settings.working_dir + filename + '.kn5'
        result = export_kn5(filepath, context)

        if result["status"] == "success":
            if result["warnings"]:
                warning_msg = f"Exported {filename}.kn5 with warnings:\n" + "\n".join(
                    result["warnings"][:3]
                )
                self.report({'WARNING'}, warning_msg)
            return True
        else:
            error_msg = f"KN5 export failed for {filename}:\n" + "\n".join(result["warnings"][:3])
            self.report({'ERROR'}, error_msg)
            return False

    def _export_fbx(self, context, settings, exp_opts, filename: str) -> bool:
        """Export single collection to FBX."""
        try:
            filepath = settings.working_dir + filename + '.fbx'
            ops.export_scene.fbx(
                filepath=filepath,
                object_types={'EMPTY','MESH'},
                global_scale=exp_opts.scale,
                apply_unit_scale=exp_opts.unit_scale,
                apply_scale_options=exp_opts.scale_options,
                use_space_transform=exp_opts.space_transform,
                use_mesh_modifiers=exp_opts.mesh_modifiers,
                axis_up=exp_opts.up,
                axis_forward=exp_opts.forward,
            )
            return True
        except Exception as e:
            self.report({'ERROR'}, f"FBX export failed for {filename}: {e}")
            return False

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

        # KN5-specific autofixes
        if settings.export_settings.use_kn5:
            from ...kn5.texture_baking import bake_all_procedural_materials

            # Bake procedural textures if found
            resolution = settings.export_settings.texture_bake_resolution
            warnings = bake_all_procedural_materials(context, resolution)
            for warning in warnings:
                self.report({'INFO'}, warning)

        return {'FINISHED'}

class AC_AddStart(Operator):
    """Add a new start position"""
    bl_idname = "ac.add_start"
    bl_label = "Add Start"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, math.pi, 0), align='CURSOR')
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        start_pos = context.object
        if not start_pos:
            return {'CANCELLED'}
        # get next start position
        start_pos.name = f"AC_START_{len(settings.get_starts(context))}"
        return {'FINISHED'}

class AC_AddHotlapStart(Operator):
    """Add a new hotlap start position"""
    bl_idname = "ac.add_hotlap_start"
    bl_label = "Add Hotlap Start"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, math.pi, 0), align='CURSOR')
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        start_pos = context.object
        if not start_pos:
            return {'CANCELLED'}
        start_pos.name = f"AC_HOTLAP_START_{len(settings.get_hotlap_starts(context))}"
        return {'FINISHED'}

class AC_AddPitbox(Operator):
    """Add a new pitbox"""
    bl_idname = "ac.add_pitbox"
    bl_label = "Add Pitbox"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        ops.object.empty_add(type='SINGLE_ARROW', scale=(2, 2, 2), rotation=(math.pi * -0.5, math.pi, 0), align='CURSOR')
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        pitbox = context.object
        if not pitbox:
            return {'CANCELLED'}
        pitbox.name = f"AC_PIT_{len(settings.get_pitboxes(context))}"
        return {'FINISHED'}

class AC_AddTimeGate(Operator):
    """Add a new time gate"""
    bl_idname = "ac.add_time_gate"
    bl_label = "Add Time Gate"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        count = len(settings.get_time_gates(context)) // 2
        ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0), align='CURSOR')
        time_gate_L = context.object
        if not time_gate_L:
            return {'CANCELLED'}
        time_gate_L.name = f"AC_TIME_{count}_L"
        ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0), align='CURSOR')
        time_gate_R = context.object
        if not time_gate_R:
            # delete the left gate if the right one fails
            ops.object.select_all(action='DESELECT')
            time_gate_L.select_set(True)
            ops.object.delete()
            return {'CANCELLED'}
        time_gate_R.name = f"AC_TIME_{count}_R"
        return {'FINISHED'}

class AC_AddABStartGate(Operator):
    """Add a new AB start gate"""
    bl_idname = "ac.add_ab_start_gate"
    bl_label = "Add AB Start Gate"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0), align='CURSOR')
        ab_start_L = context.object
        if not ab_start_L:
            return {'CANCELLED'}
        ab_start_L.name = "AC_AB_START_L"
        ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0), align='CURSOR')
        ab_start_R = context.object
        if not ab_start_R:
            # delete the left gate if the right one fails
            ops.object.select_all(action='DESELECT')
            ab_start_L.select_set(True)
            ops.object.delete()
            return {'CANCELLED'}
        ab_start_R.name = "AC_AB_START_R"
        return {'FINISHED'}

class AC_AddABFinishGate(Operator):
    """Add a new AB finish gate"""
    bl_idname = "ac.add_ab_finish_gate"
    bl_label = "Add AB Finish Gate"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(-10, 0, 0), align='CURSOR')
        ab_finish_L = context.object
        if not ab_finish_L:
            return {'CANCELLED'}
        ab_finish_L.name = "AC_AB_FINISH_L"
        ops.object.empty_add(type='CUBE', scale=(2, 2, 2), rotation=(0, 0, 0), location=(10, 0, 0), align='CURSOR')
        ab_finish_R = context.object
        if not ab_finish_R:
            # delete the left gate if the right one fails
            ops.object.select_all(action='DESELECT')
            ab_finish_L.select_set(True)
            ops.object.delete()
            return {'CANCELLED'}
        ab_finish_R.name = "AC_AB_FINISH_R"
        return {'FINISHED'}

class AC_AddAudioEmitter(Operator):
    """Add a new audio emitter"""
    bl_idname = "ac.add_audio_emitter"
    bl_label = "Add Audio Emitter"
    bl_options = {'REGISTER'}
    def execute(self, context: Context):
        settings = context.scene.AC_Settings # type: ignore
        settings.consolidate_logic_gates(context)
        ops.object.empty_add(type='SPHERE', scale=(2, 2, 2), rotation=(0, 0, 0), align='CURSOR')
        audio_emitter = context.object
        if not audio_emitter:
            return {'CANCELLED'}
        audio_emitter.name = f"AC_AUDIO_{len(settings.get_audio_emitters(context)) + 1}"
        return {'FINISHED'}
