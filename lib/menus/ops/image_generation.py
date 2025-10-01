import bpy
from bpy.types import Operator
from mathutils import Vector
import os


def calculate_track_bounds(context, use_selection=False):
    """
    Calculate bounding box of track objects

    Args:
        context: Blender context
        use_selection: If True, use selected objects. If False, use objects with ROAD surface

    Returns:
        tuple: (center: Vector, size: Vector, min: Vector, max: Vector)
    """
    objects = []

    if use_selection:
        # Use selected mesh objects
        objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not objects:
            raise RuntimeError("No mesh objects selected. Please select the main track road mesh(es).")
    else:
        # Find objects with ROAD surface assignment
        # Objects are named like: "1ROAD_main", "2ROAD_section_a"
        import re
        from ....utils.constants import SURFACE_REGEX

        for obj in context.scene.objects:
            if obj.type != 'MESH':
                continue

            match = re.match(SURFACE_REGEX, obj.name)
            if match and match.group(2) == 'ROAD':
                objects.append(obj)

        if not objects:
            raise RuntimeError(
                "No ROAD surface objects found. Please either:\n"
                "1. Select the main track road mesh(es), OR\n"
                "2. Assign ROAD surface to track meshes"
            )

    # Calculate combined bounding box
    if not objects:
        raise RuntimeError("No objects to calculate bounds from")

    # Initialize with first object bounds
    first_obj = objects[0]
    bbox_corners = [first_obj.matrix_world @ Vector(corner) for corner in first_obj.bound_box]

    min_x = min(v.x for v in bbox_corners)
    max_x = max(v.x for v in bbox_corners)
    min_y = min(v.y for v in bbox_corners)
    max_y = max(v.y for v in bbox_corners)
    min_z = min(v.z for v in bbox_corners)
    max_z = max(v.z for v in bbox_corners)

    # Expand bounds to include all objects
    for obj in objects[1:]:
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        min_x = min(min_x, min(v.x for v in bbox_corners))
        max_x = max(max_x, max(v.x for v in bbox_corners))
        min_y = min(min_y, min(v.y for v in bbox_corners))
        max_y = max(max_y, max(v.y for v in bbox_corners))
        min_z = min(min_z, min(v.z for v in bbox_corners))
        max_z = max(max_z, max(v.z for v in bbox_corners))

    min_corner = Vector((min_x, min_y, min_z))
    max_corner = Vector((max_x, max_y, max_z))
    center = (min_corner + max_corner) / 2
    size = max_corner - min_corner

    return center, size, min_corner, max_corner


def create_overhead_camera(context, center, size, padding_percent=10.0):
    """
    Create orthographic camera positioned above track

    Args:
        context: Blender context
        center: Vector - center point of track
        size: Vector - dimensions of track bounding box
        padding_percent: float - padding around track (percentage)

    Returns:
        Object: Camera object
    """
    # Create camera data
    cam_data = bpy.data.cameras.new("AC_MAP_CAMERA")
    cam_data.type = 'ORTHO'

    # Calculate orthographic scale (largest horizontal dimension + padding)
    max_dim = max(size.x, size.y)
    padding_factor = 1.0 + (padding_percent / 100.0)
    cam_data.ortho_scale = max_dim * padding_factor

    # Create camera object
    cam_obj = bpy.data.objects.new("AC_MAP_CAMERA", cam_data)
    context.scene.collection.objects.link(cam_obj)

    # Position camera above track center, looking straight down
    height = size.z + 100.0  # 100m above highest point
    cam_obj.location = Vector((center.x, center.y, height))
    cam_obj.rotation_euler = (0, 0, 0)  # Looking down -Z axis

    return cam_obj


def create_bw_material():
    """
    Create white emission material for track rendering

    Returns:
        Material: White emission material
    """
    mat = bpy.data.materials.new("AC_MAP_MATERIAL")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Emission shader (white)
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    emission.inputs['Strength'].default_value = 1.0

    # Output node
    output = nodes.new('ShaderNodeOutputMaterial')

    # Link nodes
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return mat


def apply_material_override(objects, material):
    """
    Apply material override to objects and store originals

    Args:
        objects: List of objects to override
        material: Material to apply

    Returns:
        dict: Restoration data {obj.name: [original_materials]}
    """
    restore_data = {}

    for obj in objects:
        if obj.type != 'MESH':
            continue

        # Store original materials
        original_mats = [slot.material for slot in obj.material_slots]
        restore_data[obj.name] = original_mats

        # Clear and apply override
        obj.data.materials.clear()
        if not obj.data.materials:
            obj.data.materials.append(material)
        else:
            obj.data.materials[0] = material

    return restore_data


def restore_materials(objects, restore_data):
    """
    Restore original materials to objects

    Args:
        objects: List of objects
        restore_data: dict from apply_material_override
    """
    for obj in objects:
        if obj.name not in restore_data:
            continue

        obj.data.materials.clear()
        for mat in restore_data[obj.name]:
            obj.data.materials.append(mat)


class AC_GenerateMap(Operator):
    """Generate overhead track map (map.png) and outline (outline.png)"""
    bl_idname = "ac.generate_map"
    bl_label = "Generate Map & Outline"
    bl_options = {'REGISTER', 'UNDO'}

    use_selection: bpy.props.BoolProperty(
        name="Use Selection",
        description="Use selected objects instead of ROAD surface objects",
        default=False
    )

    resolution: bpy.props.IntProperty(
        name="Resolution",
        description="Map resolution (square)",
        default=2048,
        min=512,
        max=4096
    )

    padding: bpy.props.FloatProperty(
        name="Padding",
        description="Padding around track (percentage)",
        default=10.0,
        min=0.0,
        max=50.0,
        subtype='PERCENTAGE'
    )

    def invoke(self, context, event):
        # Check if objects are selected
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if selected_meshes:
            self.use_selection = True
            return self.execute(context)
        else:
            # No selection, will use ROAD surfaces
            self.use_selection = False
            return self.execute(context)

    def _generate_map_ini(self, working_dir, width, height):
        """Generate map.ini file with correct dimensions"""
        from ....utils.files import save_ini, get_data_directory

        data_dir = get_data_directory()
        map_ini_path = os.path.join(data_dir, "map.ini")

        # Calculate offsets (center the map)
        x_offset = width // 2
        z_offset = height // 2

        map_ini_data = {
            'PARAMETERS': {
                'WIDTH': str(width),
                'HEIGHT': str(height),
                'MARGIN': '20',
                'SCALE_FACTOR': '1.0',
                'MAX_SIZE': '1600',
                'X_OFFSET': str(x_offset),
                'Z_OFFSET': str(z_offset),
                'DRAWING_SIZE': '10'
            }
        }

        save_ini(map_ini_path, map_ini_data)
        self.report({'INFO'}, f"map.ini generated: {map_ini_path}")

    def execute(self, context):
        settings = context.scene.AC_Settings

        if not settings.working_dir:
            self.report({'ERROR'}, "Working directory not set")
            return {'CANCELLED'}

        # Store original state
        original_camera = context.scene.camera
        original_render_settings = {
            'resolution_x': context.scene.render.resolution_x,
            'resolution_y': context.scene.render.resolution_y,
            'film_transparent': context.scene.render.film_transparent,
            'filepath': context.scene.render.filepath,
        }

        temp_camera = None
        temp_material = None
        restore_data = None
        track_objects = []

        try:
            # Calculate track bounds
            center, size, min_corner, max_corner = calculate_track_bounds(context, self.use_selection)

            self.report({'INFO'}, f"Track bounds: {size.x:.1f}m × {size.y:.1f}m")

            # Get track objects for material override
            if self.use_selection:
                track_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
            else:
                import re
                from ....utils.constants import SURFACE_REGEX
                track_objects = [
                    obj for obj in context.scene.objects
                    if obj.type == 'MESH' and re.match(SURFACE_REGEX, obj.name) and
                    re.match(SURFACE_REGEX, obj.name).group(2) == 'ROAD'
                ]

            # Create temporary camera
            temp_camera = create_overhead_camera(context, center, size, self.padding)
            context.scene.camera = temp_camera

            # Create and apply material override
            temp_material = create_bw_material()
            restore_data = apply_material_override(track_objects, temp_material)

            # Configure render settings
            context.scene.render.resolution_x = self.resolution
            context.scene.render.resolution_y = self.resolution
            context.scene.render.film_transparent = True  # Transparent background for mini-map

            # Set output path for map.png
            output_path = os.path.join(settings.working_dir, "map.png")
            context.scene.render.filepath = output_path

            # Render map.png
            self.report({'INFO'}, f"Rendering map ({self.resolution}x{self.resolution})...")
            bpy.ops.render.render(write_still=True)

            if not os.path.exists(output_path):
                raise RuntimeError(f"Failed to render map to {output_path}")

            self.report({'INFO'}, f"Map generated: {output_path}")

            # Generate outline.png by downscaling map.png
            self.report({'INFO'}, "Generating outline.png from map...")
            outline_path = os.path.join(settings.working_dir, "ui", "outline.png")

            # Ensure ui directory exists
            ui_dir = os.path.join(settings.working_dir, "ui")
            os.makedirs(ui_dir, exist_ok=True)

            # Load map.png image
            if "AC_TEMP_MAP" in bpy.data.images:
                bpy.data.images.remove(bpy.data.images["AC_TEMP_MAP"])

            map_image = bpy.data.images.load(output_path)
            map_image.name = "AC_TEMP_MAP"

            # Resize to 512x512 for outline
            outline_resolution = 512
            map_image.scale(outline_resolution, outline_resolution)

            # Save as outline.png
            map_image.filepath_raw = outline_path
            map_image.file_format = 'PNG'
            map_image.save()

            # Cleanup temp image
            bpy.data.images.remove(map_image)

            self.report({'INFO'}, f"Outline generated: {outline_path}")

            # Generate/update map.ini
            self.report({'INFO'}, "Generating map.ini...")
            self._generate_map_ini(settings.working_dir, self.resolution, self.resolution)

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Map generation failed: {str(e)}")
            return {'CANCELLED'}

        finally:
            # Cleanup - restore original state
            context.scene.camera = original_camera
            context.scene.render.resolution_x = original_render_settings['resolution_x']
            context.scene.render.resolution_y = original_render_settings['resolution_y']
            context.scene.render.film_transparent = original_render_settings['film_transparent']
            context.scene.render.filepath = original_render_settings['filepath']

            # Restore materials
            if restore_data and track_objects:
                restore_materials(track_objects, restore_data)

            # Delete temporary objects
            if temp_camera:
                bpy.data.objects.remove(temp_camera, do_unlink=True)
                bpy.data.cameras.remove(temp_camera.data, do_unlink=True)

            if temp_material:
                bpy.data.materials.remove(temp_material, do_unlink=True)


class AC_CreatePreviewCamera(Operator):
    """Create a camera for track preview screenshots"""
    bl_idname = "ac.create_preview_camera"
    bl_label = "Create Preview Camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Check if camera already exists
        if "AC_PREVIEW_CAMERA" in bpy.data.objects:
            self.report({'WARNING'}, "Preview camera already exists")
            # Select and make active
            cam = bpy.data.objects["AC_PREVIEW_CAMERA"]
            context.view_layer.objects.active = cam
            cam.select_set(True)
            return {'FINISHED'}

        # Create camera
        cam_data = bpy.data.cameras.new("AC_PREVIEW_CAMERA")
        cam_obj = bpy.data.objects.new("AC_PREVIEW_CAMERA", cam_data)
        context.scene.collection.objects.link(cam_obj)

        # Position camera from current viewport if in 3D view
        if context.space_data.type == 'VIEW_3D':
            # Get viewport camera matrix
            region_3d = context.space_data.region_3d
            cam_obj.matrix_world = region_3d.view_matrix.inverted()
        else:
            # Default position: above origin looking down
            cam_obj.location = (0, -20, 10)
            cam_obj.rotation_euler = (1.1, 0, 0)

        # Set camera properties
        cam_data.lens = 35  # Slightly wide angle for nice view

        # Make it active and selected
        context.view_layer.objects.active = cam_obj
        cam_obj.select_set(True)

        # Lock camera to view if in 3D viewport
        if context.space_data.type == 'VIEW_3D':
            context.space_data.camera = cam_obj
            context.space_data.region_3d.view_perspective = 'CAMERA'

        self.report({'INFO'}, "Preview camera created at current viewport position")
        return {'FINISHED'}


class AC_GeneratePreview(Operator):
    """Generate track preview screenshot (preview.png)"""
    bl_idname = "ac.generate_preview"
    bl_label = "Generate Preview"
    bl_options = {'REGISTER', 'UNDO'}

    resolution_x: bpy.props.IntProperty(
        name="Width",
        description="Preview width",
        default=1920,
        min=1280,
        max=3840
    )

    resolution_y: bpy.props.IntProperty(
        name="Height",
        description="Preview height",
        default=1080,
        min=720,
        max=2160
    )

    def execute(self, context):
        settings = context.scene.AC_Settings

        if not settings.working_dir:
            self.report({'ERROR'}, "Working directory not set")
            return {'CANCELLED'}

        # Store original render settings and camera
        original_camera = context.scene.camera
        original_render_settings = {
            'resolution_x': context.scene.render.resolution_x,
            'resolution_y': context.scene.render.resolution_y,
            'filepath': context.scene.render.filepath,
        }

        try:
            # Check for preview camera, otherwise use viewport
            preview_camera = bpy.data.objects.get("AC_PREVIEW_CAMERA")
            use_camera_render = False

            if preview_camera and preview_camera.type == 'CAMERA':
                # Use the preview camera for rendering
                context.scene.camera = preview_camera
                use_camera_render = True
                self.report({'INFO'}, "Using AC_PREVIEW_CAMERA for render")
            else:
                # Check if we're in 3D viewport for OpenGL render
                if context.space_data.type != 'VIEW_3D':
                    self.report({'ERROR'}, "Must be run from 3D viewport (or create a preview camera)")
                    return {'CANCELLED'}
                self.report({'INFO'}, "Using current viewport view for render")

            # Ensure ui directory exists
            ui_dir = os.path.join(settings.working_dir, "ui")
            os.makedirs(ui_dir, exist_ok=True)

            # Configure render settings
            context.scene.render.resolution_x = self.resolution_x
            context.scene.render.resolution_y = self.resolution_y

            # Set output path
            output_path = os.path.join(ui_dir, "preview.png")
            context.scene.render.filepath = output_path

            # Render
            self.report({'INFO'}, f"Rendering preview ({self.resolution_x}x{self.resolution_y})...")
            if use_camera_render:
                # Use full render for camera
                bpy.ops.render.render(write_still=True)
            else:
                # Use OpenGL viewport render
                bpy.ops.render.opengl(write_still=True)

            if not os.path.exists(output_path):
                raise RuntimeError(f"Failed to render preview to {output_path}")

            self.report({'INFO'}, f"Preview generated: {output_path}")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Preview generation failed: {str(e)}")
            return {'CANCELLED'}

        finally:
            # Restore original render settings and camera
            context.scene.camera = original_camera
            context.scene.render.resolution_x = original_render_settings['resolution_x']
            context.scene.render.resolution_y = original_render_settings['resolution_y']
            context.scene.render.filepath = original_render_settings['filepath']
