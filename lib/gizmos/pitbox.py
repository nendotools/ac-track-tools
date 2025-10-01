from bpy.types import Gizmo, GizmoGroup, Object
from mathutils import Matrix, Vector
import math

from ...lib.settings import AC_Settings


class AC_GizmoPitbox(Gizmo):
    bl_idname = "AC_GizmoPitbox"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    ob_name: str
    def setup(self):
        if not hasattr(self, "shape"):
            # Pitbox: box with X on ground (Z=-1) + "PIT" text on front vertical face (Y=-1)
            self.shape = self.new_custom_shape('TRIS',
            [
                # Box outline on ground (Z=-1 plane)
                # Front edge
                (-1, -1, -1), (1, -1, -1), (1, -1, -0.95),
                (-1, -1, -1), (1, -1, -0.95), (-1, -1, -0.95),
                # Back edge
                (-1, -0.5, -1), (1, -0.5, -1), (1, -0.5, -0.95),
                (-1, -0.5, -1), (1, -0.5, -0.95), (-1, -0.5, -0.95),
                # Left edge
                (-1, -1, -1), (-1, -0.5, -1), (-1, -0.5, -0.95),
                (-1, -1, -1), (-1, -0.5, -0.95), (-1, -1, -0.95),
                # Right edge
                (1, -1, -1), (1, -0.5, -1), (1, -0.5, -0.95),
                (1, -1, -1), (1, -0.5, -0.95), (1, -1, -0.95),

                # X inside box on ground (Z=-1 plane)
                # Diagonal 1: front-left to back-right
                (-0.85, -0.95, -1), (-0.75, -0.95, -1), (0.75, -0.55, -1),
                (-0.85, -0.95, -1), (0.75, -0.55, -1), (0.85, -0.55, -1),
                # Diagonal 2: front-right to back-left
                (0.85, -0.95, -1), (0.75, -0.95, -1), (-0.75, -0.55, -1),
                (0.85, -0.95, -1), (-0.75, -0.55, -1), (-0.85, -0.55, -1),

                # "PIT" text on front vertical face (Y=-1 plane, using X and Z coordinates)
                # P - vertical bar
                (-0.7, -1, -0.8), (-0.6, -1, -0.8), (-0.6, -1, 0.2),
                (-0.7, -1, -0.8), (-0.6, -1, 0.2), (-0.7, -1, 0.2),
                # P - top horizontal
                (-0.6, -1, 0.1), (-0.3, -1, 0.1), (-0.3, -1, 0.2),
                (-0.6, -1, 0.1), (-0.3, -1, 0.2), (-0.6, -1, 0.2),
                # P - middle horizontal
                (-0.6, -1, -0.1), (-0.3, -1, -0.1), (-0.3, -1, 0.0),
                (-0.6, -1, -0.1), (-0.3, -1, 0.0), (-0.6, -1, 0.0),
                # P - right vertical segment
                (-0.3, -1, -0.1), (-0.2, -1, -0.1), (-0.2, -1, 0.2),
                (-0.3, -1, -0.1), (-0.2, -1, 0.2), (-0.3, -1, 0.2),

                # I - vertical bar
                (-0.05, -1, -0.8), (0.05, -1, -0.8), (0.05, -1, 0.2),
                (-0.05, -1, -0.8), (0.05, -1, 0.2), (-0.05, -1, 0.2),

                # T - top horizontal
                (0.2, -1, 0.1), (0.7, -1, 0.1), (0.7, -1, 0.2),
                (0.2, -1, 0.1), (0.7, -1, 0.2), (0.2, -1, 0.2),
                # T - vertical bar
                (0.4, -1, -0.8), (0.5, -1, -0.8), (0.5, -1, 0.2),
                (0.4, -1, -0.8), (0.5, -1, 0.2), (0.4, -1, 0.2),
            ])
            self.scale = 4.3, 1.4, 2.3
            self.use_draw_scale = False
            self.use_draw_modal = True

    def draw(self, context):
        from gpu.state import blend_set, depth_test_set
        blend_set('ALPHA')
        depth_test_set('ALWAYS')
        self.draw_custom_shape(self.shape)
        depth_test_set('LESS_EQUAL')
        blend_set('NONE')

    def draw_select(self, context, select_id): # type: ignore
        self.draw_custom_shape(self.shape, select_id=select_id)

    def update(self, mat_location, mat_rotation):
        mat_t = Matrix.Translation(mat_location)
        mat_r = mat_rotation.to_matrix().to_4x4()
        self.matrix_basis = mat_t @ mat_r

    def invoke(self, context, event):
        # Select the parent Empty object when clicked
        ob = context.scene.objects.get(self.ob_name)
        if ob:
            # Deselect all other objects first
            for obj in context.selected_objects:
                obj.select_set(False)
            # Select and make active
            ob.select_set(True)
            context.view_layer.objects.active = ob
        return {'FINISHED'}

class AC_GizmoStartPos(Gizmo):
    bl_idname = "AC_GizmoStartPos"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    ob_name: str
    def setup(self):
        if not hasattr(self, "shape"):
            # Wide, short U-shape flat on the ground at the front
            # Like a starting line marking on track surface
            self.shape = self.new_custom_shape('TRIS',
            [
                # All geometry is on Z=-1 (ground plane)
                # Y=-1 is the front edge (starting line)

                # Left vertical bar of U (front edge)
                (-1, -1, -1), (-0.85, -1, -1), (-0.85, -0.7, -1),
                (-1, -1, -1), (-0.85, -0.7, -1), (-1, -0.7, -1),

                # Right vertical bar of U (front edge)
                (0.85, -1, -1), (1, -1, -1), (1, -0.7, -1),
                (0.85, -1, -1), (1, -0.7, -1), (0.85, -0.7, -1),

                # Bottom horizontal bar of U (connecting left and right)
                (-0.85, -0.7, -1), (0.85, -0.7, -1), (0.85, -0.85, -1),
                (-0.85, -0.7, -1), (0.85, -0.85, -1), (-0.85, -0.85, -1),

                # Inner detail lines (for visual depth)
                # Left inner line
                (-0.9, -1, -1), (-0.85, -1, -1), (-0.85, -0.75, -1),
                (-0.9, -1, -1), (-0.85, -0.75, -1), (-0.9, -0.75, -1),

                # Right inner line
                (0.85, -1, -1), (0.9, -1, -1), (0.9, -0.75, -1),
                (0.85, -1, -1), (0.9, -0.75, -1), (0.85, -0.75, -1),

                # Bottom inner line
                (-0.9, -0.75, -1), (0.9, -0.75, -1), (0.9, -0.8, -1),
                (-0.9, -0.75, -1), (0.9, -0.8, -1), (-0.9, -0.8, -1),
            ])
            self.scale = 4.3, 1.4, 2.3
            self.use_draw_scale = False
            self.use_draw_modal = True

    def draw(self, context):
        from gpu.state import blend_set, depth_test_set
        blend_set('ALPHA')
        depth_test_set('ALWAYS')
        self.draw_custom_shape(self.shape)
        depth_test_set('LESS_EQUAL')
        blend_set('NONE')

    def draw_select(self, context, select_id): # type: ignore
        self.draw_custom_shape(self.shape, select_id=select_id)

    def update(self, mat_location, mat_rotation):
        mat_t = Matrix.Translation(mat_location)
        mat_r = mat_rotation.to_matrix().to_4x4()
        self.matrix_basis = mat_t @ mat_r

    def invoke(self, context, event):
        # Select the parent Empty object when clicked
        ob = context.scene.objects.get(self.ob_name)
        if ob:
            # Deselect all other objects first
            for obj in context.selected_objects:
                obj.select_set(False)
            # Select and make active
            ob.select_set(True)
            context.view_layer.objects.active = ob
        return {'FINISHED'}

class AC_GizmoGate(Gizmo):
    bl_idname = "AC_GizmoGate"

    pos_start: tuple[float, float, float]
    pos_end: tuple[float, float, float]
    def setup(self):
        if not hasattr(self, "shape"):
            self.shape = self.new_custom_shape('LINES', [(-1, 0, 0), (1, 0, 0)])
            self.scale = 1, 1, 1
            self.use_draw_scale = False
            self.use_draw_modal = True

    def update_shape(self):
        up_vector = Vector((0, 0, 0.5))
        down_vector = Vector((0, 0, -0.5))

        self.shape = self.new_custom_shape('LINES',
            [
                self.pos_start, self.pos_end,
                self.pos_start + down_vector, self.pos_end + down_vector,
                self.pos_start + up_vector, self.pos_end + up_vector,
            ])

    def draw(self, context):
        self.draw_custom_shape(self.shape)

    def draw_select(self, context, select_id): # type: ignore
        self.draw_custom_shape(self.shape, select_id=select_id)

    def update(self, loc_start, loc_end):
        self.pos_start = loc_start
        self.pos_end = loc_end
        self.update_shape()

    def invoke(self, context, event):
        return {'FINISHED'}


class AC_GizmoGroup(GizmoGroup):
    bl_idname = "AC_GizmoGroup"
    bl_label = "AC Track Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'PERSISTENT', '3D', 'SHOW_MODAL_ALL', 'DEPTH_3D'}

    @classmethod
    def poll(cls, context): # type: ignore
        return (context.scene.objects)


    def setup(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences # type: ignore
        self.gizmos.clear()
        obs = context.scene.objects

        for ob in obs:
            if ob.type == 'EMPTY':
                if ob.name.startswith('AC_PIT_'):
                    gb = self.gizmos.new("AC_GizmoPitbox")
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                    gb.hide = not ob.visible_get() or not prefs.show_pitboxes
                    gb.color = prefs.pitbox_color[:3]
                    gb.alpha = prefs.pitbox_color[3] * 0.3  # Low opacity by default
                    gb.color_highlight = tuple(min(c * 1.3, 1.0) for c in prefs.pitbox_color[:3])
                    gb.alpha_highlight = prefs.pitbox_color[3]  # Full opacity on hover

                if ob.name.startswith('AC_START_'):
                    gb = self.gizmos.new("AC_GizmoStartPos")
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                    gb.hide = not ob.visible_get() or not prefs.show_start
                    gb.color = prefs.start_color[:3]
                    gb.alpha = prefs.start_color[3] * 0.3  # Low opacity by default
                    gb.color_highlight = tuple(min(c * 1.3, 1.0) for c in prefs.start_color[:3])
                    gb.alpha_highlight = prefs.start_color[3]  # Full opacity on hover

                if ob.name.startswith('AC_HOTLAP_START_'):
                    gb = self.gizmos.new("AC_GizmoStartPos")
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                    gb.hide = not ob.visible_get() or not prefs.show_hotlap_start
                    gb.color = prefs.hotlap_start_color[:3]
                    gb.alpha = prefs.hotlap_start_color[3] * 0.3  # Low opacity by default
                    gb.color_highlight = tuple(min(c * 1.3, 1.0) for c in prefs.hotlap_start_color[:3])
                    gb.alpha_highlight = prefs.hotlap_start_color[3]  # Full opacity on hover

    def refresh(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences # type: ignore
        obs = [ ob for ob in context.scene.objects if ob.type == 'EMPTY' and (ob.name.startswith('AC_PIT_') or ob.name.startswith('AC_START_') or ob.name.startswith('AC_HOTLAP_START_')) ]

        # Rebuild if object count changed
        main_gizmos = [g for g in self.gizmos if g.bl_idname in ['AC_GizmoPitbox', 'AC_GizmoStartPos']]
        if len(obs) != len(main_gizmos):
            self.setup(context)
            return

        # Remove all gate gizmos before creating new ones
        gate_gizmos = [g for g in self.gizmos if g.bl_idname == 'AC_GizmoGate']
        for gate_gizmo in gate_gizmos:
            self.gizmos.remove(gate_gizmo)

        for g in self.gizmos:
            if not hasattr(g, 'ob_name'):
                continue

            ob = context.scene.objects.get(g.ob_name)
            if not ob:
                g.hide = True
                continue

            # Update visibility based on object type
            if ob.name.startswith('AC_PIT_'):
                g.hide = not ob.visible_get() or not prefs.show_pitboxes
            elif ob.name.startswith('AC_START_'):
                g.hide = not ob.visible_get() or not prefs.show_start
            elif ob.name.startswith('AC_HOTLAP_START_'):
                g.hide = not ob.visible_get() or not prefs.show_hotlap_start

            # Update gizmo position
            g.update(ob.location, ob.rotation_euler)

        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        time_gates: list[list[Object]] = settings.get_time_gates(context, True) # type: ignore
        for gate in time_gates:
            if len(gate) != 2:
                continue
            g = self.gizmos.new("AC_GizmoGate")
            g.hide = not gate[0].visible_get() or not gate[1].visible_get() or not prefs.show_time_gates
            g.color = prefs.time_gate_color[:3]
            g.alpha = prefs.time_gate_color[3] * 0.3  # Low opacity by default
            g.color_highlight = prefs.time_gate_color[:3]
            g.alpha_highlight = prefs.time_gate_color[3]  # Full opacity on hover
            g.update(gate[0].location, gate[1].location)

        ab_start_gates = settings.get_ab_start_gates(context)
        if len(ab_start_gates) % 2 == 0 and len(ab_start_gates) > 0:
            g = self.gizmos.new("AC_GizmoGate")
            g.hide = not ab_start_gates[0].visible_get() or not ab_start_gates[1].visible_get() or not prefs.show_ab_start
            g.color = prefs.ab_start_color[:3]
            g.alpha = prefs.ab_start_color[3] * 0.3  # Low opacity by default
            g.color_highlight = prefs.ab_start_color[:3]
            g.alpha_highlight = prefs.ab_start_color[3]  # Full opacity on hover
            g.update(ab_start_gates[0].location, ab_start_gates[1].location)

        ab_finish_gates = settings.get_ab_finish_gates(context)
        if len(ab_finish_gates) % 2 == 0 and len(ab_finish_gates) > 0:
            g = self.gizmos.new("AC_GizmoGate")
            g.hide = not ab_finish_gates[0].visible_get() or not ab_finish_gates[1].visible_get() or not prefs.show_ab_finish
            g.color = prefs.ab_finish_color[:3]
            g.alpha = prefs.ab_finish_color[3] * 0.3  # Low opacity by default
            g.color_highlight = prefs.ab_finish_color[:3]
            g.alpha_highlight = prefs.ab_finish_color[3]  # Full opacity on hover
            g.update(ab_finish_gates[0].location, ab_finish_gates[1].location)
