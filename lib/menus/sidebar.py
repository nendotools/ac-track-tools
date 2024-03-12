from bpy.types import Panel, UIList
from ..configs.audio_source import AC_AudioSource


class VIEW3D_PT_AC_Sidebar:
    bl_label = "Assetto Corsa Configurator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Assetto Corsa'

class VIEW3D_PT_AC_Sidebar_Project(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Main"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Main"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        col = layout.column(align=True)
        col.prop(settings, "working_dir", text="Working Directory")
        if settings.working_dir:
            row = col.row()
            row.operator("ac.save_settings", text="Save Settings")
            row.separator()
            row.operator("ac.load_settings", text="Load Settings")
        else:
            row = col.row()
            row.alignment = 'CENTER'
            row.label(text="Please set a working directory")


class VIEW3D_PT_AC_Sidebar_Track(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Track"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Track"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        track = settings.track
        col = layout.column(align=True)
        col.prop(track, "name", text="Name")
        col.prop(track, "description", text="Description")
        split = col.split(factor=0.5)
        # location display
        col = split.column(align=True)
        col.prop(track, "country", text="Country")
        col.prop(track, "city", text="City")
        col = split.column(align=True)
        col.prop(track, "length", text="Length")
        col.prop(track, "width", text="Width")
        col.prop(track, "run", text="Run Type")

        # tag display
        col = layout.column(align=True)
        row = col.row()
        row.prop(track, "show_tags", text="", icon='TRIA_DOWN' if track.show_tags else 'TRIA_RIGHT', emboss=False)
        row.label(text="Tags")
        if track.show_tags:
            row = col.box().row()
            inner = row.column(align=True)
            inner.operator("ac.add_tag", text="New Tag", icon='ADD')
            inner.label(text="Searchable tags for track")
            row.template_list("AC_UL_Tags", "", track, "tags", track, "tags_index", rows=3)

        # geotag display
        col = layout.column(align=True)
        row = col.row()
        row.prop(track, "show_geotags", text="", icon='TRIA_DOWN' if track.show_geotags else 'TRIA_RIGHT', emboss=False)
        row.label(text="GeoTags")
        if track.show_geotags:
            row = col.box().row()
            inner = row.column(align=True)
            inner.operator("ac.add_geo_tag", text="New Tag", icon='ADD')
            inner.label(text="Optional Latitude, Longitude, Altitude of track")
            row.template_list("AC_UL_Tags", "", track, "geotags", track, "geotags_index", rows=3)



class AC_UL_Tags(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index): # type: ignore
        row = layout.row()
        row.prop(item, "value", text="", emboss=False)
        if(active_property == "tags_index"):
            delete = row.operator("ac.remove_tag", text="", icon='X')
            delete.index = index
        if(active_property == "geotags_index"):
            delete = row.operator("ac.remove_geo_tag", text="", icon='X')
            delete.index = index


class VIEW3D_PT_AC_Sidebar_Surfaces(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Surfaces"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Surfaces"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        if not settings.surfaces: # need to initialize surfaces before starting
            layout.operator("ac.init_surfaces", text="Init Surfaces")
            return

        assigned = settings.get_surface_groups(context)
        active = settings.active_surfaces
        for surface in settings.surfaces:
            box = layout.box()
            row = box.row()
            toggle = row.operator("ac.toggle_surface", text="", icon='TRIA_DOWN' if surface.name in active else 'TRIA_RIGHT')
            row.label(text=f"{surface.name} [{len(assigned[surface.key])}]")
            toggle.target = surface.name
            if surface.name in active:
                col = box.column(align=True)
                col.enabled = surface.custom
                col.row().prop(surface, "name", text="Name")
                col.row().prop(surface, "key", text="Key")
                if(surface.custom): # Only show these properties if the surface is custom
                    split = col.split(factor=0.5)
                    col = split.column(align=True, heading="Physics")
                    col.row().prop(surface, "friction", text="Friction", slider=True)
                    col.row().prop(surface, "damping", text="Damping", slider=True)
                    col.row().prop(surface, "sin_height", text="Sine Height", slider=True)
                    col.row().prop(surface, "sin_length", text="Sine Length", slider=True)
                    col.row().prop(surface, "vibration_gain", text="Vibration Gain", slider=True)
                    col.row().prop(surface, "vibration_length", text="Vibration Length", slider=True)

                    col = split.column(align=True)
                    col.row().label(text="Settings")
                    col.row().prop(surface, "wav", text="Wav")
                    col.row().prop(surface, "wav_pitch", text="Wav Pitch", slider=True)
                    col.row().prop(surface, "ff_effect", text="FF Effect")
                    col.row().prop(surface, "dirt_additive", text="Dirt Additive", slider=True)
                    col.row().prop(surface, "is_valid_track", text="Is Valid Track", toggle=True)
                    if(surface.is_valid_track):
                        col.row().prop(surface, "is_pit_lane", text="Is Pit Lane", toggle=True)
                    else:
                        col.row().prop(surface, "black_flag_time", text="Black Flag Time", slider=True)
                    box.separator()
                    op = box.row().operator("ac.remove_surface", text="Remove", emboss=True)
                    op.target = surface.name

        col = layout.column(align=True)
        col.separator(factor=1.5)
        row = layout.row()
        row.operator("ac.add_surface", text="New Surface", icon='ADD')

class VIEW3D_PT_AC_Sidebar_Audio(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Audio"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Audio"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        audio_sources = settings.audio_sources
        col = layout.column(align=True)
        audio: AC_AudioSource
        for audio in audio_sources:
            box = col.box()
            row = box.row()
            toggle = row.operator("ac.toggle_audio", text="", icon='TRIA_DOWN' if audio.expand else 'TRIA_RIGHT')
            row.label(text=f"{audio.name}")
            toggle.target = audio.name
            if audio.expand:
                box.row().prop(audio, "audio_type", text="Audio Type")
                box.row().prop(audio, "node", text="Emitter Node")
                col = box.column(align=True)
                if audio.audio_type == "SFX":
                    col.row().prop(audio, "filename", text="Filename")
                    col.row().prop(audio, "volume", text="Volume")
                    col.row().prop(audio, "volume_scale", text="Volume Scale")
                else:
                    col.row().prop(audio, "preset", text="Preset")
                    col.row().prop(audio, "enabled", text="Enabled")
                    col.separator()
                    col = box.column(align=True)
                    col.label(text="Reverb settings")
                    col.separator()
                    col.row().prop(audio, "min_distance", slider=True)
                    col.row().prop(audio, "max_distance", slider=True)
                    col.row().prop(audio, "decay_time", slider=True)
                    col.row().prop(audio, "late_delay", slider=True)
                    col.row().prop(audio, "hf_reference", slider=True)
                    col.row().prop(audio, "hf_decay_ratio", slider=True)
                    col.row().prop(audio, "diffusion", slider=True)
                    col.row().prop(audio, "density", slider=True)
                    col.row().prop(audio, "low_shelf_frequency", slider=True)
                    col.row().prop(audio, "low_shelf_gain", slider=True)
                    col.row().prop(audio, "high_cut", slider=True)
                    col.row().prop(audio, "early_late_mix", slider=True)
                    col.row().prop(audio, "wet_level", slider=True)
        col = layout.column(align=True)
        col.separator(factor=1.5)
        col.operator("ac.add_audio_source", text="New Audio Source", icon='ADD')
