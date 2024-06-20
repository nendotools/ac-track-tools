from bpy.types import Gizmo, GizmoGroup, Object
from mathutils import Matrix, Vector

from ...lib.settings import AC_Settings


class AC_GizmoPitbox(Gizmo):
    bl_idname = "AC_GizmoPitbox"

    ob_name: str
    def setup(self):
        if not hasattr(self, "shape"):
            self.shape = self.new_custom_shape('TRIS',
            [
                # box on bottom from -1 to 1
                (-1, -1, -1), (1, -1, -1), (1, -1, 1),
                (-1, -1, -1), (1, -1, 1), (-1, -1, 1),

                # short walls from -0.7 to -0.5 on left size
                (-1, -0.7, -1), (-1, -0.7, 1), (-1, -0.5, 1),
                (-1, -0.7, -1), (-1, -0.5, 1), (-1, -0.5, -1),
                (1, -0.7, -1), (1, -0.7, 1), (1, -0.5, 1),
                (1, -0.7, -1), (1, -0.5, 1), (1, -0.5, -1),
            ])
            self.color = (0, 0, 1)
            self.color_highlight = (0, 0, 1)
            self.alpha = 0.3
            self.alpha_highlight = 0.5
            self.scale = 4.3, 1.4, 2.3
            self.use_draw_scale = False
            self.use_draw_modal = True
            self.hide_select = True
            self.hide_keymap = True

    def draw(self, context):
        self.draw_custom_shape(self.shape)

    def draw_select(self, context, select_id): # type: ignore
        self.draw_custom_shape(self.shape, select_id=select_id)

    def update(self, mat_location, mat_rotation):
        mat_t = Matrix.Translation(mat_location)
        mat_r = mat_rotation.to_matrix().to_4x4()

        # move the gizmo to the object location 1.5m below the origin
        self.matrix_basis = mat_t @ Matrix.Translation((0, 0, 0)) @ mat_r

    def invoke(self, context, event):
        return {'FINISHED'}

class AC_GizmoStartPos(Gizmo):
    bl_idname = "AC_GizmoStartPos"

    ob_name: str
    def setup(self):
        if not hasattr(self, "shape"):
            self.shape = self.new_custom_shape('TRIS',
            [
                # short walls from -0.7 to -0.5 on sides
                (-1, -0.7, 0.5), (-1, -0.7, 1), (-1, -0.5, 1),
                (-1, -0.7, 0.5), (-1, -0.5, 1), (-1, -0.5, 0.5),
                (1, -0.7, 0.5), (1, -0.7, 1), (1, -0.5, 1),
                (1, -0.7, 0.5), (1, -0.5, 1), (1, -0.5, 0.5),

                #short wall from -0.7 to -0.5 on front
                (-1, -0.7, 1), (1, -0.7, 1), (1, -0.5, 1),
                (-1, -0.7, 1), (1, -0.5, 1), (-1, -0.5, 1),

                # copy walls to the floor below
                (-1, -1, 0.7), (1, -1, 0.7), (1, -1, 1),
                (-1, -1, 0.7), (1, -1, 1), (-1, -1, 1),

                # left wing shadow 
                (0.7, -1, 0.5), (1, -1, 0.5), (1, -1, 0.7),
                (0.7, -1, 0.5), (1, -1, 0.7), (0.7, -1, 0.7),

                # left wing shadow 
                (-0.7, -1, 0.5), (-1, -1, 0.5), (-1, -1, 0.7),
                (-0.7, -1, 0.5), (-1, -1, 0.7), (-0.7, -1, 0.7),
            ])
            self.color = (0, 1, 1)
            self.color_highlight = (0, 1, 1)
            self.alpha = 0.3
            self.alpha_highlight = 0.5
            self.scale = 4.3, 1.4, 2.3
            self.use_draw_scale = False
            self.use_draw_modal = True
            self.hide_select = True
            self.hide_keymap = True

    def draw(self, context):
        self.draw_custom_shape(self.shape)

    def draw_select(self, context, select_id): # type: ignore
        self.draw_custom_shape(self.shape, select_id=select_id)

    def update(self, mat_location, mat_rotation):
        mat_t = Matrix.Translation(mat_location)
        mat_r = mat_rotation.to_matrix().to_4x4()

        # move the gizmo to the object location 1.5m below the origin
        self.matrix_basis = mat_t @ Matrix.Translation((0, 0, 0)) @ mat_r

    def invoke(self, context, event):
        return {'FINISHED'}

class AC_GizmoGate(Gizmo):
    bl_idname = "AC_GizmoGate"
    # this gizmo is used to show the start/finish line between two objects
    # It should draw a line between the two objects
    # the color should be green
    # the alpha should be 0.5

    pos_start: tuple[float, float, float]
    pos_end: tuple[float, float, float]
    def setup(self):
        if not hasattr(self, "shape"):
            self.shape = self.new_custom_shape('LINES',
            [
                # line from -1 to 1
                (-1, 0, 0), (1, 0, 0),
            ])
            self.color = (0, 1, 0)
            self.color_highlight = (0, 1, 0)
            self.alpha = 0.5
            self.alpha_highlight = 0.5
            self.scale = 1, 1, 1
            self.use_draw_scale = False
            self.use_draw_modal = True
            self.hide_select = True
            self.hide_keymap = True

    def update_shape(self):
        up_vector = Vector((0, 0, 0.5))
        down_vector = Vector((0, 0, -0.5))

        self.shape = self.new_custom_shape('LINES',
            #line from pos_start to pos_end
            [
                self.pos_start, self.pos_end,
                # line 0.5m below and above the line
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
        self.gizmos.clear()
        # add pitbox gizmo to all empty objects
        obs = context.scene.objects
        for ob in obs:
            if ob.type == 'EMPTY':
                if ob.name.startswith('AC_PIT_'):
                    # the box should be 4.3m x 1.4m x 2.3m
                    gb = self.gizmos.new("AC_GizmoPitbox")
                    # set the gizmo location to the object location
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                if ob.name.startswith('AC_START_'):
                    # the box should be 4.3m x 1.4m x 2.3m
                    gb = self.gizmos.new("AC_GizmoStartPos")
                    # set the gizmo location to the object location
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name
                if ob.name.startswith('AC_HOTLAP_START_'):
                    # the box should be 4.3m x 1.4m x 2.3m
                    gb = self.gizmos.new("AC_GizmoStartPos")
                    gb.color = (1, 0, 0)
                    gb.color_highlight = (1, 0, 0)
                    # set the gizmo location to the object location
                    gb.matrix_basis = ob.matrix_basis.normalized()
                    gb.ob_name = ob.name

    def refresh(self, context):
        obs = [ ob for ob in context.scene.objects if ob.type == 'EMPTY' and (ob.name.startswith('AC_PIT_') or ob.name.startswith('AC_START_') or ob.name.startswith('AC_HOTLAP_START_')) ]
        if len(obs) != len(self.gizmos):
            self.setup(context)

        for g in self.gizmos:
            ob = context.scene.objects.get(g.ob_name)
            if not ob:
                continue
            g.update(ob.location, ob.rotation_euler)

        settings: AC_Settings = context.scene.AC_Settings # type: ignore
        time_gates: list[list[Object]] = settings.get_time_gates(context, True) # type: ignore
        for gate in time_gates:
            if len(gate) != 2:
                continue
            g = self.gizmos.new("AC_GizmoGate")
            g.color = (1, 1, 0.5)
            g.update(gate[0].location, gate[1].location)

        ab_start_gates = settings.get_ab_start_gates(context)
        if len(ab_start_gates) % 2 == 0:
            g = self.gizmos.new("AC_GizmoGate")
            g.color = (1, 0.2, 0.2)
            g.update(ab_start_gates[0].location, ab_start_gates[1].location)

        ab_finish_gates = settings.get_ab_finish_gates(context)
        if len(ab_finish_gates) % 2 == 0:
            g = self.gizmos.new("AC_GizmoGate")
            g.color = (0, 1, 0)
            g.update(ab_finish_gates[0].location, ab_finish_gates[1].location)
