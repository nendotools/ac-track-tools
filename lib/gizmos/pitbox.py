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
            # 3D pitbox representation: floor + walls + posts
            self.shape = self.new_custom_shape('TRIS',
            [
                # floor outline (thicker representation)
                (-1, -1, -1), (1, -1, -1), (1, -1, -0.95),
                (-1, -1, -1), (1, -1, -0.95), (-1, -1, -0.95),

                # left wall (front to back)
                (-1, -1, -1), (-1, -0.5, -1), (-1, -0.5, 1),
                (-1, -1, -1), (-1, -0.5, 1), (-1, -1, 1),
                (-1, -0.5, -1), (-0.95, -0.5, -1), (-0.95, -0.5, 1),
                (-1, -0.5, -1), (-0.95, -0.5, 1), (-1, -0.5, 1),

                # right wall (front to back)
                (1, -1, -1), (1, -0.5, -1), (1, -0.5, 1),
                (1, -1, -1), (1, -0.5, 1), (1, -1, 1),
                (0.95, -0.5, -1), (1, -0.5, -1), (1, -0.5, 1),
                (0.95, -0.5, -1), (1, -0.5, 1), (0.95, -0.5, 1),

                # back wall (left to right)
                (-1, -0.5, -1), (1, -0.5, -1), (1, -0.5, -0.95),
                (-1, -0.5, -1), (1, -0.5, -0.95), (-1, -0.5, -0.95),

                # corner posts (thicker vertical indicators)
                (-1, -1, -1), (-0.9, -1, -1), (-0.9, -1, 1),
                (-1, -1, -1), (-0.9, -1, 1), (-1, -1, 1),
                (0.9, -1, -1), (1, -1, -1), (1, -1, 1),
                (0.9, -1, -1), (1, -1, 1), (0.9, -1, 1),

                (-1, -0.6, -1), (-0.9, -0.6, -1), (-0.9, -0.6, 1),
                (-1, -0.6, -1), (-0.9, -0.6, 1), (-1, -0.6, 1),
                (0.9, -0.6, -1), (1, -0.6, -1), (1, -0.6, 1),
                (0.9, -0.6, -1), (1, -0.6, 1), (0.9, -0.6, 1),
            ])
            self.scale = 4.3, 1.4, 2.3
            self.use_draw_scale = False
            self.use_draw_modal = True
            self.use_draw_hover = True

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
            context.view_layer.objects.active = ob
            ob.select_set(True)
        return {'FINISHED'}

class AC_GizmoStartPos(Gizmo):
    bl_idname = "AC_GizmoStartPos"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )

    ob_name: str
    def setup(self):
        if not hasattr(self, "shape"):
            # 3D pole position line representation
            # Two parallel vertical bars with horizontal connecting strips
            self.shape = self.new_custom_shape('TRIS',
            [
                # left pole (vertical bar)
                (-0.9, -1, -1), (-0.7, -1, -1), (-0.7, -1, 1),
                (-0.9, -1, -1), (-0.7, -1, 1), (-0.9, -1, 1),
                (-0.9, -0.9, -1), (-0.7, -0.9, -1), (-0.7, -0.9, 1),
                (-0.9, -0.9, -1), (-0.7, -0.9, 1), (-0.9, -0.9, 1),

                # right pole (vertical bar)
                (0.7, -1, -1), (0.9, -1, -1), (0.9, -1, 1),
                (0.7, -1, -1), (0.9, -1, 1), (0.7, -1, 1),
                (0.7, -0.9, -1), (0.9, -0.9, -1), (0.9, -0.9, 1),
                (0.7, -0.9, -1), (0.9, -0.9, 1), (0.7, -0.9, 1),

                # connecting strips (horizontal bars at different heights)
                # bottom strip
                (-0.9, -1, -1), (0.9, -1, -1), (0.9, -1, -0.9),
                (-0.9, -1, -1), (0.9, -1, -0.9), (-0.9, -1, -0.9),

                # mid-low strip
                (-0.9, -1, -0.2), (0.9, -1, -0.2), (0.9, -1, -0.1),
                (-0.9, -1, -0.2), (0.9, -1, -0.1), (-0.9, -1, -0.1),

                # mid-high strip
                (-0.9, -1, 0.4), (0.9, -1, 0.4), (0.9, -1, 0.5),
                (-0.9, -1, 0.4), (0.9, -1, 0.5), (-0.9, -1, 0.5),

                # top strip
                (-0.9, -1, 0.9), (0.9, -1, 0.9), (0.9, -1, 1),
                (-0.9, -1, 0.9), (0.9, -1, 1), (-0.9, -1, 1),

                # front face depth indicators (thin connecting walls)
                (-0.9, -1, -1), (-0.9, -0.9, -1), (-0.7, -0.9, -1),
                (-0.9, -1, -1), (-0.7, -0.9, -1), (-0.7, -1, -1),
                (0.7, -1, -1), (0.7, -0.9, -1), (0.9, -0.9, -1),
                (0.7, -1, -1), (0.9, -0.9, -1), (0.9, -1, -1),

                # back face depth indicators
                (-0.9, -1, 1), (-0.9, -0.9, 1), (-0.7, -0.9, 1),
                (-0.9, -1, 1), (-0.7, -0.9, 1), (-0.7, -1, 1),
                (0.7, -1, 1), (0.7, -0.9, 1), (0.9, -0.9, 1),
                (0.7, -1, 1), (0.9, -0.9, 1), (0.9, -1, 1),
            ])
            self.scale = 4.3, 1.4, 2.3
            self.use_draw_scale = False
            self.use_draw_modal = True
            self.use_draw_hover = True

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
            context.view_layer.objects.active = ob
            ob.select_set(True)
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


class AC_GizmoAnchor(Gizmo):
    """Clickable anchor point for manipulating empties"""
    bl_idname = "AC_GizmoAnchor"

    ob_name: str
    anchor_type: str  # 'center', 'front', 'back', 'left', 'right'

    def setup(self):
        if not hasattr(self, "shape"):
            # Create a small sphere anchor
            segments = 8
            verts = []

            # Simple octahedron for performance
            verts = [
                (0, 0, 0.3), (0, 0, -0.3),
                (0.3, 0, 0), (-0.3, 0, 0),
                (0, 0.3, 0), (0, -0.3, 0),
            ]

            # Create triangles connecting the vertices
            self.shape = self.new_custom_shape('TRIS', [
                # top pyramid
                verts[0], verts[2], verts[4],
                verts[0], verts[4], verts[3],
                verts[0], verts[3], verts[5],
                verts[0], verts[5], verts[2],
                # bottom pyramid
                verts[1], verts[4], verts[2],
                verts[1], verts[3], verts[4],
                verts[1], verts[5], verts[3],
                verts[1], verts[2], verts[5],
            ])
            self.use_draw_scale = False
            self.use_draw_modal = True
            self.use_draw_hover = True

    def draw(self, context):
        from gpu.state import blend_set, depth_test_set
        blend_set('ALPHA')
        depth_test_set('ALWAYS')
        self.draw_custom_shape(self.shape)
        depth_test_set('LESS_EQUAL')
        blend_set('NONE')

    def draw_select(self, context, select_id): # type: ignore
        self.draw_custom_shape(self.shape, select_id=select_id)

    def update(self, mat_location, mat_rotation, offset):
        """Update anchor position with offset based on anchor type"""
        mat_t = Matrix.Translation(mat_location)
        mat_r = mat_rotation.to_matrix().to_4x4()

        # Apply offset based on anchor type
        local_offset = Vector(offset)
        offset_matrix = Matrix.Translation(mat_r @ local_offset)

        self.matrix_basis = mat_t @ offset_matrix

    def invoke(self, context, event):
        # Select the parent Empty object when clicked
        ob = context.scene.objects.get(self.ob_name)
        if ob:
            context.view_layer.objects.active = ob
            ob.select_set(True)
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

    def _add_anchors(self, ob, color, show):
        """Add anchor points for an object"""
        if not show:
            return

        # Define anchor positions relative to object
        anchor_positions = {
            'center': (0, 0, 0),
            'front': (0, 2, 0),
            'back': (0, -2, 0),
            'top': (0, 0, 2),
        }

        for anchor_type, offset in anchor_positions.items():
            anchor = self.gizmos.new("AC_GizmoAnchor")
            anchor.ob_name = ob.name
            anchor.anchor_type = anchor_type
            anchor.hide = not ob.visible_get()

            # Brighten anchor color for visibility
            anchor_color = tuple(min(c * 1.5, 1.0) for c in color[:3])
            anchor.color = anchor_color
            anchor.alpha = color[3] * 0.8
            anchor.color_highlight = (1.0, 1.0, 0.0)
            anchor.alpha_highlight = 1.0

            anchor.update(ob.location, ob.rotation_euler, offset)

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
                    gb.alpha = prefs.pitbox_color[3]
                    gb.color_highlight = tuple(min(c * 1.3, 1.0) for c in prefs.pitbox_color[:3])
                    gb.alpha_highlight = min(prefs.pitbox_color[3] * 1.2, 1.0)

                    self._add_anchors(ob, prefs.pitbox_color, prefs.show_pitboxes)

                if ob.name.startswith('AC_START_'):
                    gb = self.gizmos.new("AC_GizmoStartPos")
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                    gb.hide = not ob.visible_get() or not prefs.show_start
                    gb.color = prefs.start_color[:3]
                    gb.alpha = prefs.start_color[3]
                    gb.color_highlight = tuple(min(c * 1.3, 1.0) for c in prefs.start_color[:3])
                    gb.alpha_highlight = min(prefs.start_color[3] * 1.2, 1.0)

                    self._add_anchors(ob, prefs.start_color, prefs.show_start)

                if ob.name.startswith('AC_HOTLAP_START_'):
                    gb = self.gizmos.new("AC_GizmoStartPos")
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                    gb.hide = not ob.visible_get() or not prefs.show_hotlap_start
                    gb.color = prefs.hotlap_start_color[:3]
                    gb.alpha = prefs.hotlap_start_color[3]
                    gb.color_highlight = tuple(min(c * 1.3, 1.0) for c in prefs.hotlap_start_color[:3])
                    gb.alpha_highlight = min(prefs.hotlap_start_color[3] * 1.2, 1.0)

                    self._add_anchors(ob, prefs.hotlap_start_color, prefs.show_hotlap_start)

    def refresh(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences # type: ignore
        obs = [ ob for ob in context.scene.objects if ob.type == 'EMPTY' and (ob.name.startswith('AC_PIT_') or ob.name.startswith('AC_START_') or ob.name.startswith('AC_HOTLAP_START_')) ]

        # Rebuild if object count changed
        main_gizmos = [g for g in self.gizmos if g.bl_idname in ['AC_GizmoPitbox', 'AC_GizmoStartPos']]
        if len(obs) != len(main_gizmos):
            self.setup(context)
            return

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
            if g.bl_idname == "AC_GizmoAnchor":
                # Get anchor offset based on type
                anchor_positions = {
                    'center': (0, 0, 0),
                    'front': (0, 2, 0),
                    'back': (0, -2, 0),
                    'top': (0, 0, 2),
                }
                offset = anchor_positions.get(g.anchor_type, (0, 0, 0))
                g.update(ob.location, ob.rotation_euler, offset)
            else:
                g.update(ob.location, ob.rotation_euler)

        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        time_gates: list[list[Object]] = settings.get_time_gates(context, True) # type: ignore
        for gate in time_gates:
            if len(gate) != 2:
                continue
            g = self.gizmos.new("AC_GizmoGate")
            g.hide = not gate[0].visible_get() or not gate[1].visible_get() or not prefs.show_time_gates
            g.color = prefs.time_gate_color[:3]
            g.alpha = prefs.time_gate_color[3]
            g.color_highlight = prefs.time_gate_color[:3]
            g.alpha_highlight = prefs.time_gate_color[3]
            g.update(gate[0].location, gate[1].location)

        ab_start_gates = settings.get_ab_start_gates(context)
        if len(ab_start_gates) % 2 == 0 and len(ab_start_gates) > 0:
            g = self.gizmos.new("AC_GizmoGate")
            g.hide = not ab_start_gates[0].visible_get() or not ab_start_gates[1].visible_get() or not prefs.show_ab_start
            g.color = prefs.ab_start_color[:3]
            g.alpha = prefs.ab_start_color[3]
            g.color_highlight = prefs.ab_start_color[:3]
            g.alpha_highlight = prefs.ab_start_color[3]
            g.update(ab_start_gates[0].location, ab_start_gates[1].location)

        ab_finish_gates = settings.get_ab_finish_gates(context)
        if len(ab_finish_gates) % 2 == 0 and len(ab_finish_gates) > 0:
            g = self.gizmos.new("AC_GizmoGate")
            g.hide = not ab_finish_gates[0].visible_get() or not ab_finish_gates[1].visible_get() or not prefs.show_ab_finish
            g.color = prefs.ab_finish_color[:3]
            g.alpha = prefs.ab_finish_color[3]
            g.color_highlight = prefs.ab_finish_color[:3]
            g.alpha_highlight = prefs.ab_finish_color[3]
            g.update(ab_finish_gates[0].location, ab_finish_gates[1].location)
