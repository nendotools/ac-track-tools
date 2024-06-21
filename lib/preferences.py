# type: ignore
from bpy.props import BoolProperty, FloatVectorProperty
from bpy.types import AddonPreferences


class AC_Preferences(AddonPreferences):
    bl_idname = __package__.split('.')[0]

    show_start: BoolProperty(
        name="Show Start",
        default=True,
        update=lambda s, c: s.refresh_gizmos(c),
    )
    start_color: FloatVectorProperty(
        name="Start Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=lambda s, c: s.refresh_gizmos(c),
    )

    show_hotlap_start: BoolProperty(
        name="Show Hotlap Start",
        default=True,
        update=lambda s, c: s.refresh_gizmos(c),
    )
    hotlap_start_color: FloatVectorProperty(
        name="Hotlap Start Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0, 1.0),
        update=lambda s, c: s.refresh_gizmos(c),
    )

    show_ab_start: BoolProperty(
        name="Show AB Start",
        default=True,
        update=lambda s, c: s.refresh_gizmos(c),
    )
    ab_start_color: FloatVectorProperty(
        name="AB Start Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=lambda s, c: s.refresh_gizmos(c),
    )

    show_ab_finish: BoolProperty(
        name="Show AB Finish",
        default=True,
        update=lambda s, c: s.refresh_gizmos(c),
    )
    ab_finish_color: FloatVectorProperty(
        name="AB Finish Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=lambda s, c: s.refresh_gizmos(c),
    )

    show_time_gates: BoolProperty(
        name="Show Time Gates",
        default=True,
        update=lambda s, c: s.refresh_gizmos(c),
    )
    time_gate_color: FloatVectorProperty(
        name="Time Gate Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=lambda s, c: s.refresh_gizmos(c),
    )

    show_pitboxes: BoolProperty(
        name="Show Pitboxes",
        default=True,
        update=lambda s, c: s.refresh_gizmos(c),
    )
    pitbox_color: FloatVectorProperty(
        name="Pitbox Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=lambda s, c: s.refresh_gizmos(c),
    )

    # lazy refresh method to force redrawing gizmos
    def refresh_gizmos(self, context):
        obj = context.scene.objects[0]
        obj.select_set(obj.select_get())

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Track Node Colors")
        row = box.split(factor=0.3)
        row.prop(self, "show_start", toggle=True)
        if self.show_start:
            row.prop(self, "start_color", icon_only=True)
        else:
            row.label(text="disabled")

        row = box.split(factor=0.3)
        row.prop(self, "show_hotlap_start", toggle=True)
        if self.show_hotlap_start:
            row.prop(self, "hotlap_start_color", icon_only=True)
        else:
            row.label(text="disabled")

        row = box.split(factor=0.3)
        row.prop(self, "show_ab_start", toggle=True)
        if self.show_ab_start:
            row.prop(self, "ab_start_color", icon_only=True)
        else:
            row.label(text="disabled")

        row = box.split(factor=0.3)
        row.prop(self, "show_ab_finish", toggle=True)
        if self.show_ab_finish:
            row.prop(self, "ab_finish_color", icon_only=True)
        else:
            row.label(text="disabled")

        row = box.split(factor=0.3)
        row.prop(self, "show_time_gates", toggle=True)
        if self.show_time_gates:
            row.prop(self, "time_gate_color", icon_only=True)
        else:
            row.label(text="disabled")

        row = box.split(factor=0.3)
        row.prop(self, "show_pitboxes", toggle=True)
        if self.show_pitboxes:
            row.prop(self, "pitbox_color", icon_only=True)
        else:
            row.label(text="disabled")
