from bpy.types import Panel, UIList


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
            col.operator("ac.save_settings", text="Save Settings")
            col.operator("ac.load_settings", text="Load Settings")
        else:
            col.label(text="Please set a working directory")


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
        # add tags
        split = col.split(factor=0.5)
        # location data
        col = split.column(align=True)
        col.prop(track, "country", text="Country")
        col.prop(track, "city", text="City")
        col = split.column(align=True)
        col.prop(track, "length", text="Length")
        col.prop(track, "width", text="Width")
        col.prop(track, "run", text="Run")

        # show existing tags
        col = layout.column(align=True)
        row = col.row()
        row.label(text="Tags")
        row.prop(track, "show_tags", text="", icon='TRIA_DOWN' if track.show_tags else 'TRIA_LEFT', emboss=False)
        if track.show_tags:
            row = col.box().row()
            inner = row.column(align=True)
            inner.operator("ac.add_tag", text="New Tag", icon='ADD')
            row.template_list("AC_UL_Tags", "", track, "tags", track, "tags_index", rows=3)

        col = layout.column(align=True)
        row = col.row()
        row.label(text="GeoTags")
        row.prop(track, "show_geotags", text="", icon='TRIA_DOWN' if track.show_geotags else 'TRIA_LEFT', emboss=False)
        if track.show_geotags:
            row = col.box().row()
            inner = row.column(align=True)
            inner.operator("ac.add_geo_tag", text="New Tag", icon='ADD')
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
            row.label(text=f"{surface.name} [{len(assigned[surface.key])}]")
            toggle = row.operator("ac.toggle_surface", text="", icon='TRIA_DOWN' if surface.name in active else 'TRIA_RIGHT')
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
