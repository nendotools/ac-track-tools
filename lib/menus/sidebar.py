import bpy
from bpy.types import Context, Panel, UILayout, UIList

from ..configs.audio_source import AC_AudioSource
from ..settings import AC_Settings


class AC_UL_Tags(UIList):
    layout_type = "COMPACT"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_property, index
    ):  # type: ignore
        row = layout.row()
        row.prop(item, "value", text="", emboss=False)
        if active_property == "tags_index":
            delete = row.operator("ac.remove_tag", text="", icon="X")
            delete.index = index
        if active_property == "geotags_index":
            delete = row.operator("ac.remove_geo_tag", text="", icon="X")
            delete.index = index

    def draw_filter(self, context: Context, layout: UILayout):  # type: ignore
        pass


class AC_UL_Extensions(UIList):
    layout_type = "COMPACT"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_property, index
    ):  # type: ignore
        row = layout.row()
        attr = row.split(factor=0.3)
        attr.prop(item, "key", text="", emboss=False)
        sub = attr.row()
        sub.prop(item, "value", text="", emboss=False)
        delete = row.operator("ac.global_remove_extension_item", text="", icon="X")
        delete.ext_index = int(self.list_id.split("-")[-1])
        delete.item_index = index

    def draw_filter(self, context, layout):
        pass


class AC_UL_SurfaceExtensions(UIList):
    layout_type = "COMPACT"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_property, index
    ):  # type: ignore
        row = layout.split(factor=0.3)
        row.prop(item, "key", text="", emboss=False)
        sub = row.row()
        sub.prop(item, "value", text="", emboss=False)
        delete = sub.operator("ac.delete_surface_ext", text="", icon="X")
        delete.extension = data.name
        delete.index = index

    def draw_filter(self, context, layout):
        pass


class VIEW3D_PT_AC_Sidebar:
    bl_label = "Assetto Corsa Configurator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Assetto Corsa: Track"


class VIEW3D_PT_AC_Sidebar_Project(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Main"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Main"
    bl_context = "objectmode"

    def draw(self, context):
        import bpy
        layout = self.layout
        settings: AC_Settings = context.scene.AC_Settings  # type: ignore
        col = layout.column(align=True)
        # If the working directory is the same as the blend file, it will return //, which is not a valid path
        # So we should validate it and set it to the blend file directory if it is invalid
        col.prop(settings, "working_dir", text="Working Directory")

        has_working_dir = bool(settings.working_dir)
        is_blend_saved = bpy.data.is_saved
        can_save_or_export = has_working_dir and is_blend_saved

        if settings.working_dir:
            row = col.row()
            save_btn = row.row()
            save_btn.enabled = can_save_or_export
            save_btn.operator("ac.save_settings", text="Save Settings")
            row.separator()
            row.operator("ac.load_settings", text="Load Settings")

            if not is_blend_saved:
                info_row = col.row()
                info_row.alignment = "CENTER"
                info_row.label(text="Save blend file to enable saving/export", icon="ERROR")
        else:
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="Please set a working directory")

        col.separator(factor=1.5)
        errors = settings.run_preflight(context)
        can_fix = len([error for error in errors if error["severity"] == 1]) > 0

        # Preflight checks header
        row = col.row()
        row.label(text="Track Preflight Checks")
        row.separator()
        r = row.row()
        r.enabled = can_fix
        r.operator(
            "ac.autofix_preflight",
            text="Fix Errors",
            icon="FAKE_USER_OFF" if can_fix else "FAKE_USER_ON",
        )

        # Status box
        box = col.box()
        if len(errors) == 0:
            box.label(text="Ready for Export!", icon="CHECKMARK")
        else:
            for error in errors:
                icon = (
                    "CANCEL"
                    if error["severity"] == 2
                    else "ERROR"
                    if error["severity"] == 1
                    else "OUTLINER_OB_LIGHT"
                )
                box.label(text=error["message"], icon=icon)

        # Export section
        col.separator(factor=1.5)
        export_box = col.box()
        opts = settings.export_settings

        # Export header with collapse toggle
        row = export_box.row()
        row.prop(
            settings,
            "show_export",
            icon_only=True,
            toggle=True,
            emboss=False,
            icon="TRIA_DOWN" if settings.show_export else "TRIA_RIGHT",
        )
        row.label(text="Export Settings")

        # Expanded settings
        if settings.show_export:
            # Format selector - labeled radio buttons
            format_row = export_box.row(align=True)
            format_row.label(text="Format:")
            format_buttons = format_row.row(align=True)
            fbx_btn = format_buttons.row(align=True)
            fbx_btn.prop(opts, "use_kn5", text="FBX", toggle=True, invert_checkbox=True)
            kn5_btn = format_buttons.row(align=True)
            kn5_btn.prop(opts, "use_kn5", text="KN5", toggle=True)
            export_box.separator(factor=0.5)
            settings_box = export_box.box()
            settings_box.use_property_split = True
            settings_box.use_property_decorate = False

            # FBX-specific options
            if not opts.use_kn5:
                settings_box.label(text="FBX Settings:", icon="EXPORT")
                settings_box.prop(opts, "up")
                settings_box.prop(opts, "forward")
                settings_box.prop(opts, "scale", slider=True)
                settings_box.prop(opts, "unit_scale")
                settings_box.prop(opts, "space_transform")
                settings_box.prop(opts, "mesh_modifiers")
                settings_box.prop(opts, "scale_options")

            # KN5-specific options
            else:
                settings_box.label(text="KN5 Settings:", icon="EXPORT")
                settings_box.prop(opts, "bake_procedural_textures")
                if opts.bake_procedural_textures:
                    settings_box.prop(opts, "texture_bake_resolution")

        # Export button outside box
        col.separator(factor=0.5)
        export_row = col.row()
        # Only block export on severity 1 (fixable) and 2 (critical) errors, not severity 0 (warnings)
        blocking_errors = [e for e in errors if e["severity"] >= 1]
        export_row.enabled = len(blocking_errors) == 0 and can_save_or_export
        export_text = f"Export Track to {'KN5' if opts.use_kn5 else 'FBX'}"
        export_row.operator("ac.export_track", text=export_text, icon="EXPORT")


class VIEW3D_PT_AC_Sidebar_Track(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Track"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Track"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings  # type: ignore
        track = settings.track
        col = layout.column(align=True)
        col.prop(track, "name", text="Name")
        col.prop(track, "description", text="Description")
        split = col.split(factor=0.5)
        # location display
        col = split.column(align=True)
        col.prop(track, "country", text="Country")
        col.prop(track, "city", text="City")
        row = col.split(factor=0.23)
        row.label(text="Pitboxes:")
        row.prop(track, "pitboxes", text="", slider=True)
        col = split.column(align=True)
        col.prop(track, "length", text="Length")
        col.prop(track, "width", text="Width")
        col.prop(track, "run", text="Run Type")

        # Track Images section
        if settings.working_dir:
            layout.separator(factor=1.5)
            box = layout.box()
            row = box.row()
            row.label(text="Track Images", icon="IMAGE_DATA")
            box.separator(factor=0.3)

            # Check which files exist
            import os
            map_exists = os.path.exists(os.path.join(settings.working_dir, "map.png"))
            outline_exists = os.path.exists(os.path.join(settings.working_dir, "ui", "outline.png"))
            preview_exists = os.path.exists(os.path.join(settings.working_dir, "ui", "preview.png"))

            # Status indicators in compact row
            status_row = box.row(align=True)
            status_row.label(text="map.png", icon="CHECKMARK" if map_exists else "CANCEL")
            status_row.label(text="outline.png", icon="CHECKMARK" if outline_exists else "CANCEL")
            status_row.label(text="preview.png", icon="CHECKMARK" if preview_exists else "CANCEL")

            box.separator(factor=0.5)

            # Generation buttons
            row = box.row(align=True)
            row.operator("ac.generate_map", text="Generate Map & Outline", icon="IMAGE_DATA")

            # Preview camera management
            preview_cam_exists = "AC_PREVIEW_CAMERA" in context.scene.objects
            row = box.row(align=True)
            if not preview_cam_exists:
                row.operator("ac.create_preview_camera", text="Create Preview Camera", icon="OUTLINER_OB_CAMERA")
            else:
                row.label(text="Preview Camera Ready", icon="CAMERA_DATA")

            row = box.row(align=True)
            row.operator("ac.generate_preview", text="Generate Preview", icon="RENDER_STILL")

        # tag display
        col = layout.column(align=True)
        row = col.row()
        row.prop(
            track,
            "show_tags",
            text="",
            icon="TRIA_DOWN" if track.show_tags else "TRIA_RIGHT",
            emboss=False,
        )
        row.label(text="Tags")
        if track.show_tags:
            row = col.box().row()
            inner = row.column(align=True)
            inner.operator("ac.add_tag", text="New Tag", icon="ADD")
            inner.label(text="Searchable tags for track")
            row.template_list(
                "AC_UL_Tags", "tags", track, "tags", track, "tags_index", rows=3
            )

        # geotag display
        col = layout.column(align=True)
        row = col.row()
        row.prop(
            track,
            "show_geotags",
            text="",
            icon="TRIA_DOWN" if track.show_geotags else "TRIA_RIGHT",
            emboss=False,
        )
        row.label(text="GeoTags")
        if track.show_geotags:
            row = col.box().row()
            inner = row.column(align=True)
            inner.operator("ac.add_geo_tag", text="New Tag", icon="ADD")
            inner.label(text="Optional Latitude, Longitude, Altitude of track")
            row.template_list(
                "AC_UL_Tags",
                "geotags",
                track,
                "geotags",
                track,
                "geotags_index",
                rows=3,
            )


class VIEW3D_PT_AC_Sidebar_Surfaces(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Surfaces"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Surfaces"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings  # type: ignore
        if not settings.surfaces:  # need to initialize surfaces before starting
            layout.operator("ac.init_surfaces", text="Init Surfaces")
            return

        assigned = settings.get_surface_groups(context)
        active = settings.active_surfaces
        for surface in settings.get_surfaces():
            box = layout.box()
            row = box.row()
            toggle = row.operator(
                "ac.toggle_surface",
                text="",
                icon="TRIA_DOWN" if surface.name in active else "TRIA_RIGHT",
            )
            toggle.target = surface.name
            row.label(text=f"{surface.name} [{len(assigned[surface.key])}]")
            copy_surface = row.operator("ac.add_surface", text="", icon="COPYDOWN")
            copy_surface.copy_from = surface.key
            select_all = row.operator(
                "ac.select_all_surfaces", text="", icon="RESTRICT_SELECT_OFF"
            )
            select_all.surface = surface.key
            if surface.name in active:
                col = box.column(align=True)
                col.enabled = surface.custom
                col.row().prop(surface, "name", text="Name")
                col.row().prop(surface, "key", text="Key")
                if (
                    surface.custom
                ):  # Only show these properties if the surface is custom
                    split = col.split(factor=0.5)
                    col = split.column(align=True)
                    col.label(text="Settings")
                    col.row().prop(
                        surface, "is_valid_track", text="Is Valid Track", toggle=True
                    )
                    if surface.is_valid_track:
                        col.row().prop(
                            surface, "is_pit_lane", text="Is Pit Lane", toggle=True
                        )
                    else:
                        col.row().prop(
                            surface,
                            "black_flag_time",
                            text="Black Flag Time",
                            slider=True,
                        )
                    col.separator(factor=1.2)
                    col.row().prop(
                        surface, "dirt_additive", text="Dirt Additive", slider=True
                    )
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
                    col.row().prop(
                        surface, "sin_height", text="Sine Height", slider=True
                    )
                    col.row().prop(
                        surface, "sin_length", text="Sine Length", slider=True
                    )
                    col.separator(factor=1.2)
                    col.row().prop(
                        surface, "vibration_gain", text="Vibration Gain", slider=True
                    )
                    col.row().prop(
                        surface,
                        "vibration_length",
                        text="Vibration Length",
                        slider=True,
                    )
                    box.separator()
                    op = box.row().operator(
                        "ac.remove_surface", text="Remove", emboss=True
                    )
                    op.target = surface.name

        col = layout.column(align=True)
        col.separator(factor=1.5)
        row = layout.row()
        self.show_extensions(context, layout)
        layout.operator("ac.add_surface", text="New Surface", icon="ADD")

    def show_extensions(self, context, layout):
        settings = context.scene.AC_Settings
        extensions = settings.surface_ext
        if not extensions:
            return

        for extension in extensions:
            box = layout.box()
            row = box.row()
            row.label(text=f"{extension.name}")
            box.template_list(
                "AC_UL_SurfaceExtenstions",
                "",
                extension,
                "items",
                extension,
                "index",
                rows=3,
            )
            box.separator()
            ext = box.operator("ac.add_surface_ext", text="Add Extension", icon="ADD")
            ext.extension = extension.name


## TODO: Add Audio Source as fixed type (don't allow changing from SFX to REVERB)
class VIEW3D_PT_AC_Sidebar_Audio(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Audio"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Audio"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings  # type: ignore
        audio_sources = settings.audio_sources
        main_list = layout.column(align=True)
        audio: AC_AudioSource
        for audio in audio_sources:
            aud_wrap = main_list.box()
            row = aud_wrap.row()
            toggle = row.operator(
                "ac.toggle_audio",
                text="",
                icon="TRIA_DOWN" if audio.expand else "TRIA_RIGHT",
            )
            row.label(text=f"{audio.name}")
            toggle.target = audio.name
            if audio.expand:
                aud_wrap.row().prop(
                    audio, "node_pointer", text="Emitter Node", icon="NODE"
                )
                if audio.audio_type == "SFX":
                    aud_wrap.row().prop(audio, "filename", text="Filename")
                    col = aud_wrap.column(align=True)
                    row = col.row()
                    row.label(text="note: audio files must be in a sound bank to work")
                    row.alignment = "RIGHT"
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
        sfx = row.operator("ac.add_audio_source", text="New SFX Source", icon="ADD")
        sfx.audio_type = "SFX"
        reverb = row.operator(
            "ac.add_audio_source", text="New Reverb Source", icon="ADD"
        )
        reverb.audio_type = "REVERB"


class VIEW3D_PT_AC_Sidebar_Lighting(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Lighting"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Lighting"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings  # type: ignore
        light_settings = settings.lighting

        sun_section = layout.box().split(factor=0.3)
        sun_section.column(align=True).label(text="Sun Settings")
        sun = light_settings.sun
        col = sun_section.column(align=True)
        col.label(
            text="Time of Day: "
            + (
                "Sunrise"
                if sun.sun_pitch_angle < 20
                else "Sunset"
                if sun.sun_pitch_angle > 160
                else "Mid-day"
            )
        )
        col.prop(sun, "sun_pitch_angle", text="Sun Pitch Angle", slider=True)
        col.separator()

        cardinal_headings = [
            "North",
            "North-East",
            "East",
            "South-East",
            "South",
            "South-West",
            "West",
            "North-West",
        ]
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
        row.prop(
            global_lighting,
            "enable_trees_lighting",
            text="Disabled" if not global_lighting.enable_trees_lighting else "Enabled",
            toggle=True,
        )

        row = global_section.split(factor=0.3)
        row.prop(
            global_lighting,
            "use_track_ambient_ground_mult",
            text="Use Track Ambient Ground Mult",
            toggle=True,
        )
        row.prop(
            global_lighting,
            "track_ambient_ground_mult",
            text="Track Ambient Ground Mult",
            slider=True,
            emboss=global_lighting.use_track_ambient_ground_mult,
        )

        row = global_section.split(factor=0.3)
        row.prop(
            global_lighting, "use_multipliers", text="Use Multipliers", toggle=True
        )
        col = row.column(align=True)
        col.prop(
            global_lighting,
            "lit_mult",
            text="Lit Multiplier",
            slider=True,
            emboss=global_lighting.use_multipliers,
        )
        col.prop(
            global_lighting,
            "specular_mult",
            text="Specular Multiplier",
            slider=True,
            emboss=global_lighting.use_multipliers,
        )
        col.prop(
            global_lighting,
            "car_lights_lit_mult",
            text="Car Lights Lit Multiplier",
            slider=True,
            emboss=global_lighting.use_multipliers,
        )

        row = global_section.split(factor=0.3)
        row.prop(
            global_lighting,
            "use_bounced_light_mult",
            text="Use Bounced Light Mult",
            toggle=True,
        )
        row.prop(
            global_lighting,
            "bounced_light_mult",
            text="Bounced Light Mult",
            slider=True,
            emboss=global_lighting.use_bounced_light_mult,
        )

        row = global_section.split(factor=0.3)
        row.prop(
            global_lighting,
            "use_terrain_shadows_threshold",
            text="Use Terrain Shadows Threshold",
            toggle=True,
        )
        row.prop(
            global_lighting,
            "terrain_shadows_threshold",
            text="Terrain Shadows Threshold",
            slider=True,
            emboss=global_lighting.use_terrain_shadows_threshold,
        )

        for light in light_settings.lights:
            light_section = layout.box()
            header = light_section.split(factor=0.3)
            row = header.row()
            row.prop(
                light,
                "expand",
                text="",
                icon="TRIA_DOWN" if light.expand else "TRIA_RIGHT",
            )
            row.label(text=f"{str(light.light_type).title()} Light")
            header.prop(
                light,
                "active",
                text="Enabled" if light.active else "Disabled",
                toggle=True,
            )
            if light.expand:
                # light settings by section: description + type, position + direction + mesh/material, color, extras, shadow
                section = light_section.split(factor=0.3)
                section.column(align=True).label(text="Description")
                col = section.column(align=True)
                col.prop(light, "description", text="")
                col.prop(light, "light_type", text="Type", expand=False)

                section = light_section.split(factor=0.3)
                section.column(align=True).label(text="Position")
                col = section.column(align=True)
                if light.light_type == "SPOT":
                    row = col.split(factor=0.8)
                    col = row.column(align=True)
                    col.prop(light, "position", text="Coordinates")
                    col = row.column(align=True)
                    col.prop(light, "direction", text="")
                elif light.light_type == "MESH":
                    col.prop(light, "mesh", text="Mesh")
                    row = col.row()
                    row.prop(light, "position", text="Offset", slider=True)
                    row.prop(light, "direction", text="Direction")
                elif light.light_type == "LINE":
                    # line from, line to
                    col.prop(light, "line_from", text="From")
                    col.prop(light, "line_to", text="To")
                # TODO: handle light series

                section = light_section.split(factor=0.3)
                row = section.column(align=True).row()
                row.prop(
                    light,
                    "modify_shape",
                    text="",
                    toggle=True,
                    icon="TRIA_DOWN" if light.modify_shape else "TRIA_RIGHT",
                )
                row.label(text="Shape")
                if light.modify_shape:
                    col = section.column(align=True)
                    col.prop(light, "spot", text="Spotlight Radius", slider=True)
                    col.prop(
                        light,
                        "spot_sharpness",
                        text="Spotlight Edge Sharpness",
                        slider=True,
                    )
                    col.prop(light, "range", slider=True)
                    col.prop(
                        light,
                        "range_gradient_offset",
                        text="Range Gradient Offset",
                        slider=True,
                    )
                    col.prop(light, "fade_at", text="Fade At", slider=True)
                    col.prop(light, "fade_smooth", text="Fade Smooth", slider=True)

                section = light_section.split(factor=0.3)
                row = section.column(align=True).row()
                row.prop(
                    light,
                    "modify_color",
                    text="",
                    toggle=True,
                    icon="TRIA_DOWN" if light.modify_color else "TRIA_RIGHT",
                )
                row.label(text="Color")
                if light.modify_color:
                    col = section.column(align=True)
                    col.prop(light, "color", text="Color")
                    col.prop(
                        light,
                        "specular_multiplier",
                        text="Specular Multiplier",
                        slider=True,
                    )
                    col.prop(
                        light, "single_frequency", text="Single Frequency", toggle=True
                    )
                    col.prop(
                        light,
                        "diffuse_concentration",
                        text="Diffuse Concentration",
                        slider=True,
                    )

                section = light_section.split(factor=0.3)
                row.label(text="Condition")
                row = section.column(align=True).row()
                row.prop(
                    light,
                    "use_condition",
                    text="",
                    toggle=True,
                    icon="TRIA_DOWN" if light.use_condition else "TRIA_RIGHT",
                )
                if light.use_condition:
                    col = section.column(align=True)
                    col.prop(light, "condition", text="")
                    col.prop(light, "condition_offset", text="Offset", slider=True)


class VIEW3D_PT_AC_Sidebar_Extensions(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Extensions"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Extensions"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings  # type: ignore
        extensions = settings.global_extensions
        for i, extension in enumerate(extensions):
            box = layout.box()
            row = box.row()
            toggle = row.operator(
                "ac.global_toggle_extension",
                text="",
                icon="TRIA_DOWN" if extension.expand else "TRIA_RIGHT",
            )
            toggle.index = i
            row.prop(
                extension, "name", text="", emboss=True if extension.expand else False
            )
            if extension.expand:
                box.template_list(
                    "AC_UL_Extensions",
                    f"{extension.name}-{i}",
                    extension,
                    "items",
                    extension,
                    "index",
                    rows=3,
                )
                delete = box.operator(
                    "ac.global_remove_extension", text="Delete Config Group", icon="X"
                )
                delete.name = extension.name
        layout.separator(factor=1.2)
        layout.operator("ac.global_add_extension", text="Add Extension", icon="ADD")


class AC_UL_LayoutCollections(UIList):
    """UIList for layout collections - displays scene collections dynamically"""
    layout_type = "COMPACT"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_property, index
    ):
        # item is a bpy.data.collections entry
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        if not layout_settings.layouts:
            return

        active_layout = layout_settings.layouts[layout_settings.active_layout_index]
        is_enabled = active_layout.get_collection_enabled(item.name)

        # Make entire row clickable for toggling (except "default" collection)
        if item.name == "default":
            # Default collection - show as locked, always checked
            row = layout.row()
            row.enabled = False
            row.operator(
                "ac.toggle_layout_collection",
                text=item.name,
                icon="CHECKBOX_HLT",
                emboss=False
            ).collection_name = item.name
        else:
            # Other collections - entire row is an operator
            op = layout.operator(
                "ac.toggle_layout_collection",
                text=item.name,
                icon="CHECKBOX_HLT" if is_enabled else "CHECKBOX_DEHLT",
                emboss=False
            )
            op.collection_name = item.name


class VIEW3D_PT_AC_Sidebar_Layouts(VIEW3D_PT_AC_Sidebar, Panel):
    bl_label = "Layouts"
    bl_idname = "VIEW3D_PT_AC_Sidebar_Layouts"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings  # type: ignore
        layout_settings = settings.layout_settings

        # Layouts list with inline actions
        if layout_settings.layouts:
            box = layout.box()

            # Header row with Add button
            header = box.row()
            header.label(text="Track Layouts", icon='PACKAGE')
            header.operator("ac.add_layout", text="", icon="ADD")

            # Layout list
            for i, layout_item in enumerate(layout_settings.layouts):
                row = box.row(align=True)

                # Layout selector button (full width if default, partial if deletable)
                if i == 0:
                    # Default layout - no delete button, full width
                    op = row.operator(
                        "ac.set_active_layout",
                        text=layout_item.name,
                        depress=(i == layout_settings.active_layout_index),
                        icon='LOCKED' if i == 0 else 'NONE'
                    )
                    op.layout_index = str(i)
                else:
                    # Non-default layouts - split with delete button
                    split = row.split(factor=0.85, align=True)
                    op = split.operator(
                        "ac.set_active_layout",
                        text=layout_item.name,
                        depress=(i == layout_settings.active_layout_index)
                    )
                    op.layout_index = str(i)

                    # Delete button (only for non-default layouts)
                    delete_btn = split.operator(
                        "ac.remove_layout_by_index",
                        text="",
                        icon="TRASH"
                    )
                    delete_btn.layout_index = str(i)

            # Active layout collections section
            active_layout = layout_settings.layouts[layout_settings.active_layout_index]
            layout.separator(factor=0.5)

            col_box = layout.box()
            col_header = col_box.row()
            col_header.label(text="Collections", icon='OUTLINER_COLLECTION')
            col_header.label(text=f"({active_layout.name})")

            # Preview mode toggle as icon button
            col_header.prop(
                layout_settings,
                "preview_mode",
                text="",
                icon="HIDE_OFF" if layout_settings.preview_mode else "HIDE_ON",
                toggle=True
            )

            # Collections UIList
            col_box.template_list(
                "AC_UL_LayoutCollections",
                "",
                bpy.data,
                "collections",
                layout_settings,
                "collection_list_index",
                rows=4,
            )
        else:
            # No layouts - show add button
            layout.operator("ac.add_layout", text="Add Layout", icon="ADD")
