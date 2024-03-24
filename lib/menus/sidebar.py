from bpy.types import OperatorProperties, Panel, UIList
from ..configs.audio_source import AC_AudioSource

class AC_UL_Tags(UIList):
    layout_type = 'COMPACT'
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index): # type: ignore
        row = layout.row()
        row.prop(item, "value", text="", emboss=False)
        if(active_property == "tags_index"):
            delete = row.operator("ac.remove_tag", text="", icon='X')
            delete.index = index
        if(active_property == "geotags_index"):
            delete = row.operator("ac.remove_geo_tag", text="", icon='X')
            delete.index = index

    def draw_filter(self, context, layout):
        pass

class AC_UL_Extenstions(UIList):
    layout_type = 'COMPACT'
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index): # type: ignore
        row = layout.row()
        attr = row.split(factor=0.3)
        attr.prop(item, "key", text="", emboss=False)
        sub = attr.row()
        sub.prop(item, "value", text="", emboss=False)
        delete = row.operator("ac.global_remove_extension_item", text="", icon='X')
        delete.ext_index = int(self.list_id.split('-')[-1])
        delete.item_index = index

    def draw_filter(self, context, layout):
        pass

class AC_UL_SurfaceExtenstions(UIList):
    layout_type = 'COMPACT'
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index): # type: ignore
        row = layout.split(factor=0.3)
        row.prop(item, "key", text="", emboss=False)
        sub = row.row()
        sub.prop(item, "value", text="", emboss=False)
        delete = sub.operator("ac.delete_surface_ext", text="", icon='X')
        delete.extension = data.name
        delete.index = index

    def draw_filter(self, context, layout):
        pass


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
            row.template_list("AC_UL_Tags", "tags", track, "tags", track, "tags_index", rows=3)

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
            row.template_list("AC_UL_Tags", "geotags", track, "geotags", track, "geotags_index", rows=3)


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
        for surface in settings.get_surfaces():
            box = layout.box()
            row = box.row()
            toggle = row.operator("ac.toggle_surface", text="", icon='TRIA_DOWN' if surface.name in active else 'TRIA_RIGHT')
            toggle.target = surface.name
            row.label(text=f"{surface.name} [{len(assigned[surface.key])}]")
            copy_surface = row.operator("ac.add_surface", text="", icon='COPYDOWN')
            copy_surface.copy_from = surface.key
            select_all = row.operator("ac.select_all_surfaces", text="", icon='RESTRICT_SELECT_OFF')
            select_all.surface = surface.key
            if surface.name in active:
                col = box.column(align=True)
                col.enabled = surface.custom
                col.row().prop(surface, "name", text="Name")
                col.row().prop(surface, "key", text="Key")
                if(surface.custom): # Only show these properties if the surface is custom
                    split = col.split(factor=0.5)
                    col = split.column(align=True)
                    col.label(text="Settings")
                    col.row().prop(surface, "is_valid_track", text="Is Valid Track", toggle=True)
                    if(surface.is_valid_track):
                        col.row().prop(surface, "is_pit_lane", text="Is Pit Lane", toggle=True)
                    else:
                        col.row().prop(surface, "black_flag_time", text="Black Flag Time", slider=True)
                    col.separator(factor=1.2)
                    col.row().prop(surface, "dirt_additive", text="Dirt Additive", slider=True)
                    col.separator(factor=2)
                    col.label(text="Sound")
                    col.row().prop(surface, "wav", text="Wav")
                    col.separator(factor=1.2)
                    col.row().prop(surface, "wav_pitch", text="Wav Pitch", slider=True)

                    col = split.column(align=True)
                    col.label(text="Physics")
                    col.row().prop(surface, "friction", text="Friction", slider=True)
                    col.row().prop(surface, "damping", text="Damping", slider=True)
                    col.separator(factor=1.5)
                    col.label(text="Feedback")
                    col.row().prop(surface, "ff_effect", text="FF Effect")
                    col.separator(factor=1.2)
                    col.row().prop(surface, "sin_height", text="Sine Height", slider=True)
                    col.row().prop(surface, "sin_length", text="Sine Length", slider=True)
                    col.separator(factor=1.2)
                    col.row().prop(surface, "vibration_gain", text="Vibration Gain", slider=True)
                    col.row().prop(surface, "vibration_length", text="Vibration Length", slider=True)
                    box.separator()
                    op = box.row().operator("ac.remove_surface", text="Remove", emboss=True)
                    op.target = surface.name

        col = layout.column(align=True)
        col.separator(factor=1.5)
        row = layout.row()
        self.show_extensions(context, layout)
        layout.operator("ac.add_surface", text="New Surface", icon='ADD')

    def show_extensions(self, context, layout):
        settings = context.scene.AC_Settings
        extensions = settings.surface_ext
        if not extensions:
            return

        for extension in extensions:
            box = layout.box()
            row = box.row()
            row.label(text=f"{extension.name}")
            box.template_list("AC_UL_SurfaceExtenstions", "", extension, "items", extension, "index", rows=3)
            box.separator()
            ext = box.operator("ac.add_surface_ext", text="Add Extension", icon='ADD')
            ext.extension = extension.name


## TODO: Add Audio Source as fixed type (don't allow changing from SFX to REVERB)
class VIEW3D_PT_AC_Sidebar_Audio(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Audio"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Audio"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        audio_sources = settings.audio_sources
        main_list = layout.column(align=True)
        audio: AC_AudioSource
        for audio in audio_sources:
            aud_wrap = main_list.box()
            row = aud_wrap.row()
            toggle = row.operator("ac.toggle_audio", text="", icon='TRIA_DOWN' if audio.expand else 'TRIA_RIGHT')
            row.label(text=f"{audio.name}")
            toggle.target = audio.name
            if audio.expand:
                aud_wrap.row().prop(audio, "node_pointer", text="Emitter Node", icon='NODE')
                if audio.audio_type == "SFX":
                    aud_wrap.row().prop(audio, "filename", text="Filename")
                    col = aud_wrap.column(align=True)
                    row = col.row()
                    row.label(text="note: audio files must be in a sound bank to work")
                    row.alignment = 'RIGHT'
                    col.separator()
                    aud_wrap.row().prop(audio, "volume", slider=True)
                    aud_wrap.row().prop(audio, "volume_scale", slider=True)
                else:
                    row.row().prop(audio, "enabled", toggle=True)
                    row.separator()
                    row = aud_wrap.column(align=True)
                    row = row.box().column(align=True)
                    row.label(text="Reverb settings")
                    row.row().prop(audio, "preset", text="Apply a Preset")
                    row.separator()
                    row.row().prop(audio, "min_distance", slider=True)
                    row.row().prop(audio, "max_distance", slider=True)
                    row.row().prop(audio, "decay_time", slider=True)
                    row.row().prop(audio, "late_delay", slider=True)
                    row.row().prop(audio, "hf_reference", slider=True)
                    row.row().prop(audio, "hf_decay_ratio", slider=True)
                    row.row().prop(audio, "diffusion", slider=True)
                    row.row().prop(audio, "density", slider=True)
                    row.row().prop(audio, "low_shelf_frequency", slider=True)
                    row.row().prop(audio, "low_shelf_gain", slider=True)
                    row.row().prop(audio, "high_cut", slider=True)
                    row.row().prop(audio, "early_late_mix", slider=True)
                    row.row().prop(audio, "wet_level", slider=True)
                    layout.separator()
                main_list.separator(factor=1.5)
        main_list = layout.column(align=True)
        main_list.separator(factor=1.5)
        row = main_list.row()
        sfx = row.operator("ac.add_audio_source", text="New SFX Source", icon='ADD')
        sfx.audio_type = "SFX"
        reverb = row.operator("ac.add_audio_source", text="New Reverb Source", icon='ADD')
        reverb.audio_type = "REVERB"

class VIEW3D_PT_AC_Sidebar_Lighting(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Lighting"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Lighting"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        light_settings = settings.lighting

        sun_section = layout.box().split(factor=0.3)
        sun_section.column(align=True).label(text="Sun Settings")
        sun = light_settings.sun
        col = sun_section.column(align=True)
        col.label(text="Time of Day: " + ("Sunrise" if sun.sun_pitch_angle < 20 else "Sunset" if sun.sun_pitch_angle > 160 else "Mid-day"))
        col.prop(sun, "sun_pitch_angle", text="Sun Pitch Angle", slider=True)
        col.separator()

        cardinal_headings = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
        xy_headings = ["+Y", "+X +Y", "+X", "+X -Y", "-Y", "-X -Y", "-X", "-X +Y"]
        dir_index = int((sun.sun_heading_angle + 90) % 360 / 45)
        col.label(text=f"Sunrise Cardinal Direction: {cardinal_headings[dir_index]}")
        col.label(text=f"Sunrise Euclidean Direction: {xy_headings[dir_index]}")
        col.prop(sun, "sun_heading_angle", text="Sun Heading Angle", slider=True)

        global_section = layout.box()
        row = global_section.split(factor=0.3)
        row.column(align=True).label(text="Global Lighting")

        global_lighting = light_settings.global_lighting
        row = global_section.split(factor=0.3)
        row.column(align=True).label(text="Tree Lighting")
        row.prop(global_lighting, "enable_trees_lighting", text="Disabled" if not global_lighting.enable_trees_lighting else "Enabled", toggle=True)

        row = global_section.split(factor=0.3)
        row.prop(global_lighting, "use_track_ambient_ground_mult", text="Use Track Ambient Ground Mult", toggle=True)
        row.prop(global_lighting, "track_ambient_ground_mult", text="Track Ambient Ground Mult", slider=True, emboss=global_lighting.use_track_ambient_ground_mult)

        row = global_section.split(factor=0.3)
        row.prop(global_lighting, "use_multipliers", text="Use Multipliers", toggle=True)
        col = row.column(align=True)
        col.prop(global_lighting, "lit_mult", text="Lit Multiplier", slider=True, emboss=global_lighting.use_multipliers)
        col.prop(global_lighting, "specular_mult", text="Specular Multiplier", slider=True, emboss=global_lighting.use_multipliers)
        col.prop(global_lighting, "car_lights_lit_mult", text="Car Lights Lit Multiplier", slider=True, emboss=global_lighting.use_multipliers)

        row = global_section.split(factor=0.3)
        row.prop(global_lighting, "use_bounced_light_mult", text="Use Bounced Light Mult", toggle=True)
        row.prop(global_lighting, "bounced_light_mult", text="Bounced Light Mult", slider=True, emboss=global_lighting.use_bounced_light_mult)

        row = global_section.split(factor=0.3)
        row.prop(global_lighting, "use_terrain_shadows_threshold", text="Use Terrain Shadows Threshold", toggle=True)
        row.prop(global_lighting, "terrain_shadows_threshold", text="Terrain Shadows Threshold", slider=True, emboss=global_lighting.use_terrain_shadows_threshold)

        for light in light_settings.lights:
            light_section = layout.box()
            header = light_section.split(factor=0.3)
            row = header.row()
            row.prop(light, "expand", text="", icon='TRIA_DOWN' if light.expand else 'TRIA_RIGHT')
            row.label(text=f"{str(light.light_type).title()} Light")
            header.prop(light, "active", text="Enabled" if light.active else "Disabled", toggle=True)
            if light.expand:
                # light settings by section: description + type, position + direction + mesh/material, color, extras, shadow
                section = light_section.split(factor=0.3)
                section.column(align=True).label(text="Description")
                col = section.column(align=True)
                col.prop(light, "description", text="")
                col.prop(light, "light_type", text="Type", expand=False)


class VIEW3D_PT_AC_Sidebar_Extensions(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Extensions"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Extensions"
    bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings # type: ignore
        extensions = settings.global_extensions
        for i, extension in enumerate(extensions):
            box = layout.box()
            row = box.row()
            toggle = row.operator("ac.global_toggle_extension", text="", icon='TRIA_DOWN' if extension.expand else 'TRIA_RIGHT')
            toggle.index = i
            row.prop(extension, "name", text="", emboss=True if extension.expand else False)
            if extension.expand:
                box.template_list("AC_UL_Extenstions", f"{extension.name}-{i}", extension, "items", extension, "index", rows=3)
                delete = box.operator("ac.global_remove_extension", text="Delete Config Group", icon='X')
                delete.name = extension.name
        layout.separator(factor=1.2)
        layout.operator("ac.global_add_extension", text="Add Extension", icon='ADD')
