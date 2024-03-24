import re

from bpy.types import Menu, UILayout

from ...utils.constants import SURFACE_VALID_KEY
from ..configs.surface import AC_Surface


class WM_MT_AssignSurface(Menu):
    bl_label = "Assign Surface"
    bl_idname = "WM_MT_AssignSurface"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.AC_Settings
        surface: AC_Surface
        for surface in settings.get_surfaces():
            if not re.match(SURFACE_VALID_KEY, surface.key):
                layout.label(text=f"Invalid surface key: {surface.key}")
                continue
            op = layout.operator("ac.assign_surface", text=surface.name)
            op.key = surface.key
        if len(settings.surfaces) == 0:
            layout.label(text="No surfaces available")

def start_menu(self, context):
    settings = context.scene.AC_Settings
    layout: UILayout = self.layout
    layout.separator()
    if settings.track.run in ['A2B','B2A']:
        if not settings.get_ab_start_gates(context):
            layout.operator("ac.add_ab_start_gate")
        if not settings.get_ab_finish_gates(context):
            layout.operator("ac.add_ab_finish_gate")
    else: # default should be standard circuit setup
        layout.operator("ac.add_start")
        layout.operator("ac.add_hotlap_start")
        layout.operator('ac.add_time_gate')

def pit_menu(self, context):
    layout: UILayout = self.layout
    layout.separator()
    layout.operator("ac.add_pitbox")

def surface_menu(self, context):
    layout: UILayout = self.layout
    if len(context.selected_objects) == 0: # only show the menu if an object is selected
        return
    objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
    if len(objects) == 0: # only show the menu if a mesh object is selected
        return
    layout.separator()
    layout.menu("WM_MT_AssignSurface")
    layout.operator("ac.assign_wall")

def utility_menu(self, context):
    layout: UILayout = self.layout
    layout.separator()
    layout.operator("ac.assign_phys_prop")
    layout.operator("ac.add_audio_emitter")
