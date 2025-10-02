from __future__ import annotations

from typing import TYPE_CHECKING

import bmesh
from mathutils import Matrix

from .constants import MAX_VERTICES_PER_MESH, NODE_TYPES
from .kn5_writer import KN5Writer
from .utils import convert_matrix, convert_vector3

if TYPE_CHECKING:
    from bpy.types import Context, Object


class Vertex:
    """Represents a vertex with position, normal, UV, and tangent data."""

    def __init__(
        self,
        position: tuple[float, float, float],
        normal: tuple[float, float, float],
        uv: tuple[float, float],
        tangent: tuple[float, float, float],
    ):
        self.position = position
        self.normal = normal
        self.uv = uv
        self.tangent = tangent
        self._hash: int | None = None

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(
                (
                    self.position[0],
                    self.position[1],
                    self.position[2],
                    self.normal[0],
                    self.normal[1],
                    self.normal[2],
                    self.uv[0],
                    self.uv[1],
                    self.tangent[0],
                    self.tangent[1],
                    self.tangent[2],
                )
            )
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vertex):
            return False
        return (
            self.position == other.position
            and self.normal == other.normal
            and self.uv == other.uv
            and self.tangent == other.tangent
        )


class MeshData:
    """Represents geometry data for a single mesh: material, vertices, indices."""

    def __init__(self, material_id: int, vertices: list[Vertex], indices: list[int]):
        self.material_id = material_id
        self.vertices = vertices
        self.indices = indices


class NodeProperties:
    """KN5 node properties (LOD, shadows, visibility, etc.)."""

    def __init__(self, obj: Object):
        ac_kn5 = obj.AC_KN5
        self.name = obj.name
        self.lod_in: float = ac_kn5.lod_in
        self.lod_out: float = ac_kn5.lod_out
        self.layer: int = 0
        self.cast_shadows: bool = ac_kn5.cast_shadows
        self.visible: bool = ac_kn5.visible
        self.transparent: bool = ac_kn5.transparent
        self.renderable: bool = ac_kn5.renderable


class NodeWriter(KN5Writer):
    """Writes scene hierarchy and mesh data to KN5 file."""

    def __init__(self, file, context: Context, material_writer, warnings: list[str]):
        super().__init__(file)
        self.context = context
        self.material_writer = material_writer
        self.warnings = warnings

    def write(self) -> None:
        """Write scene hierarchy starting from root node."""
        self._write_root_node()
        root_objects = self._get_visible_root_objects()
        for obj in sorted(root_objects, key=lambda k: len(k.children)):
            self._write_object(obj)

    def _get_visible_root_objects(self) -> list:
        """Get root objects that are visible (not in hidden collections)."""
        visible_objects = []
        for obj in self.context.scene.objects:
            # Skip if object has parent
            if obj.parent:
                continue
            # Skip if object name starts with __
            if obj.name.startswith("__"):
                continue
            # Skip instancer objects (tree/grass scatter systems)
            if obj.name.startswith("KSTREE_GROUP_") or obj.name.startswith("GRASS_"):
                continue
            # Skip template/example objects (profiles, colliders, etc.)
            name_lower = obj.name.lower()
            if "_profile" in name_lower or "_example" in name_lower or "collider" in name_lower:
                continue
            # Skip if object is in a hidden collection
            if self._is_object_hidden(obj):
                continue
            visible_objects.append(obj)
        return visible_objects

    def _is_object_hidden(self, obj: Object) -> bool:
        """Check if object is in any hidden collection."""
        for collection in obj.users_collection:
            if collection.hide_viewport:
                return True
        return False

    def _write_root_node(self) -> None:
        """Write root 'BlenderFile' node containing all top-level objects."""
        root_children = self._get_visible_root_objects()
        self._write_node_type("Node")
        self.write_string("BlenderFile")
        self.write_uint(len(root_children))
        self.write_bool(True)  # active
        self.write_matrix(Matrix())

    def _write_object(self, obj: Object) -> None:
        """Recursively write object hierarchy."""
        if obj.type in ("MESH", "CURVE", "SURFACE"):
            if obj.children:
                msg = f"Mesh object '{obj.name}' cannot have children in KN5 format"
                raise ValueError(msg)
            self._write_mesh_node(obj)
        else:
            self._write_container_node(obj)

        for child in obj.children:
            if not child.name.startswith("__"):
                self._write_object(child)

    def _write_container_node(self, obj: Object) -> None:
        """Write non-mesh container node (empty, armature, etc.)."""
        child_count = sum(1 for child in obj.children if not child.name.startswith("__"))
        self._write_node_type("Node")
        self.write_string(obj.name)
        self.write_uint(child_count)
        self.write_bool(True)  # active
        self.write_matrix(convert_matrix(obj.matrix_local))

    def _write_mesh_node(self, obj: Object) -> None:
        """
        Write mesh node with geometry data.

        Splits mesh by material and vertex count limits.
        """
        mesh_parts = self._split_mesh_by_materials(obj)
        mesh_parts = self._split_by_vertex_limit(mesh_parts)

        if obj.parent or len(mesh_parts) > 1:
            transform = Matrix()
            if obj.parent:
                transform = convert_matrix(obj.matrix_local)

            self._write_node_type("Node")
            self.write_string(obj.name)
            self.write_uint(len(mesh_parts))
            self.write_bool(True)  # active
            self.write_matrix(transform)

        node_props = NodeProperties(obj)
        for mesh_data in mesh_parts:
            self._write_mesh_geometry(obj, mesh_data, node_props)

    def _write_node_type(self, node_type: str) -> None:
        """Write node type identifier."""
        self.write_uint(NODE_TYPES[node_type])

    def _write_mesh_geometry(self, obj: Object, mesh_data: MeshData, props: NodeProperties) -> None:
        """Write mesh geometry data: vertices, indices, bounding sphere."""
        self._write_node_type("Mesh")
        self.write_string(obj.name)
        self.write_uint(0)  # child_count (meshes cannot have children)
        self.write_bool(True)  # active
        self.write_bool(props.cast_shadows)
        self.write_bool(props.visible)
        self.write_bool(props.transparent)

        if len(mesh_data.vertices) > MAX_VERTICES_PER_MESH:
            msg = f"Mesh '{obj.name}' has {len(mesh_data.vertices)} vertices (max {MAX_VERTICES_PER_MESH})"
            raise ValueError(msg)

        self.write_uint(len(mesh_data.vertices))
        for vertex in mesh_data.vertices:
            self.write_vector3(vertex.position)
            self.write_vector3(vertex.normal)
            self.write_vector2(vertex.uv)
            self.write_vector3(vertex.tangent)

        self.write_uint(len(mesh_data.indices))
        for index in mesh_data.indices:
            self.write_ushort(index)

        if mesh_data.material_id is None:
            self.warnings.append(f"No material assigned to mesh '{obj.name}'")
            self.write_uint(0)
        else:
            self.write_uint(mesh_data.material_id)

        self.write_uint(props.layer)
        self.write_float(props.lod_in)
        self.write_float(props.lod_out)
        self._write_bounding_sphere(mesh_data.vertices)
        self.write_bool(props.renderable)

    def _write_bounding_sphere(self, vertices: list[Vertex]) -> None:
        """Calculate and write bounding sphere (center + radius)."""
        if not vertices:
            self.write_vector3((0.0, 0.0, 0.0))
            self.write_float(0.0)
            return

        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')

        for vertex in vertices:
            pos = vertex.position
            min_x = min(min_x, pos[0])
            max_x = max(max_x, pos[0])
            min_y = min(min_y, pos[1])
            max_y = max(max_y, pos[1])
            min_z = min(min_z, pos[2])
            max_z = max(max_z, pos[2])

        center = (
            min_x + (max_x - min_x) / 2,
            min_y + (max_y - min_y) / 2,
            min_z + (max_z - min_z) / 2,
        )

        radius = max((max_x - min_x) / 2, (max_y - min_y) / 2, (max_z - min_z) / 2) * 2

        self.write_vector3(center)
        self.write_float(radius)

    def _split_mesh_by_materials(self, obj: Object) -> list[MeshData]:
        """
        Split mesh into separate parts per material.

        Triangulates mesh, calculates tangents, and converts to AC coordinates.
        """
        mesh_parts = []

        # Use depsgraph to get evaluated mesh with modifiers applied and materials preserved
        depsgraph = self.context.evaluated_depsgraph_get()
        object_eval = obj.evaluated_get(depsgraph)
        mesh_copy = self.context.blend_data.meshes.new_from_object(object_eval)

        bm = bmesh.new()
        try:
            bm.from_mesh(mesh_copy)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(mesh_copy)
        finally:
            bm.free()

        try:
            mesh_copy.calc_loop_triangles()

            # Only calculate tangents if mesh has UV layers
            if mesh_copy.uv_layers:
                mesh_copy.calc_tangents()

            mesh_vertices = mesh_copy.vertices[:]
            mesh_loops = mesh_copy.loops[:]
            mesh_triangles = mesh_copy.loop_triangles[:]
            uv_layer = mesh_copy.uv_layers.active
            transform = obj.matrix_world

            if not mesh_copy.materials:
                msg = f"Object '{obj.name}' has no material assigned"
                raise ValueError(msg)

            used_materials = {tri.material_index for tri in mesh_triangles}
            for mat_index in used_materials:
                material = mesh_copy.materials[mat_index]
                if not material:
                    msg = f"Material slot {mat_index} for object '{obj.name}' has no material"
                    raise ValueError(msg)

                if material.name.startswith("__"):
                    msg = f"Material '{material.name}' is ignored but used by '{obj.name}'"
                    raise ValueError(msg)

                vertices: dict[Vertex, int] = {}
                indices: list[int] = []

                for triangle in mesh_triangles:
                    if triangle.material_index != mat_index:
                        continue

                    face_indices = []
                    for loop_index in triangle.loops:
                        loop = mesh_loops[loop_index]
                        vertex_index = loop.vertex_index

                        world_pos = transform @ mesh_vertices[vertex_index].co
                        ac_pos = convert_vector3(world_pos)
                        ac_normal = convert_vector3(loop.normal)

                        uv = (0.0, 0.0)
                        if uv_layer:
                            uv_data = uv_layer.data[loop_index].uv
                            uv = (uv_data[0], -uv_data[1])
                        else:
                            uv = self._calculate_uv_fallback(obj, mesh_copy, mat_index, world_pos)

                        ac_tangent = convert_vector3(loop.tangent)

                        vertex = Vertex(ac_pos, ac_normal, uv, ac_tangent)
                        if vertex not in vertices:
                            vertices[vertex] = len(vertices)
                        face_indices.append(vertices[vertex])

                    indices.extend([face_indices[1], face_indices[2], face_indices[0]])

                sorted_vertices = [v for v, _ in sorted(vertices.items(), key=lambda k: k[1])]
                material_id = self.material_writer.get_material_id(material)
                mesh_parts.append(MeshData(material_id, sorted_vertices, indices))

        finally:
            # Clean up temporary mesh data
            self.context.blend_data.meshes.remove(mesh_copy)

        return mesh_parts

    def _calculate_uv_fallback(
        self, obj: Object, mesh, material_index: int, world_pos
    ) -> tuple[float, float]:
        """
        Calculate UVs for meshes without UV layer.

        Uses object dimensions for basic planar projection.
        """
        size = obj.dimensions
        x = world_pos[0] / size[0] if size[0] > 0 else 0.0
        y = world_pos[1] / size[1] if size[1] > 0 else 0.0

        return (x, y)

    def _split_by_vertex_limit(self, mesh_parts: list[MeshData]) -> list[MeshData]:
        """
        Split meshes exceeding vertex limit into multiple parts.

        KN5 format has a hard limit of 65536 vertices per mesh.
        """
        result = []
        limit = MAX_VERTICES_PER_MESH

        for mesh_data in mesh_parts:
            if len(mesh_data.vertices) <= limit:
                result.append(mesh_data)
                continue

            start_index = 0
            while start_index < len(mesh_data.indices):
                vertex_mapping: dict[int, int] = {}
                new_indices = []

                for i in range(start_index, len(mesh_data.indices), 3):
                    start_index += 3
                    face = mesh_data.indices[i : i + 3]

                    for old_index in face:
                        if old_index not in vertex_mapping:
                            vertex_mapping[old_index] = len(vertex_mapping)
                        new_indices.append(vertex_mapping[old_index])

                    if len(vertex_mapping) >= limit - 3:
                        break

                new_vertices = [mesh_data.vertices[old_idx] for old_idx, _ in sorted(vertex_mapping.items(), key=lambda k: k[1])]
                result.append(MeshData(mesh_data.material_id, new_vertices, new_indices))

        return result
