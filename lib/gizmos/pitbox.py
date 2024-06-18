from bpy.types import Gizmo, GizmoGroup
from mathutils import Matrix


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
