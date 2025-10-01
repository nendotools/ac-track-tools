from __future__ import annotations

from mathutils import Matrix, Quaternion, Vector


def convert_vector3(blender_vec: Vector) -> Vector:
    """
    Convert Blender Z-up vector to Assetto Corsa Y-up coordinate system.

    Blender uses:  X=right, Y=forward, Z=up
    AC uses:       X=right, Y=up,      Z=forward

    Transformation: (X, Y, Z) → (X, Z, -Y)

    Args:
        blender_vec: Blender Vector in Z-up coordinates

    Returns:
        Vector in AC Y-up coordinates
    """
    return Vector((blender_vec[0], blender_vec[2], -blender_vec[1]))


def convert_quaternion(blender_quat: Quaternion) -> Quaternion:
    """
    Convert Blender Z-up quaternion to AC Y-up coordinate system.

    Args:
        blender_quat: Blender Quaternion rotation

    Returns:
        Quaternion in AC Y-up coordinates
    """
    axis, angle = blender_quat.to_axis_angle()
    axis = convert_vector3(axis)
    return Quaternion(axis, angle)


def convert_matrix(blender_matrix: Matrix) -> Matrix:
    """
    Convert Blender Z-up transformation matrix to AC Y-up coordinate system.

    Decomposes into translation, rotation, scale, converts each component,
    then rebuilds the matrix in AC's coordinate system.

    Args:
        blender_matrix: Blender 4x4 transformation matrix

    Returns:
        Matrix in AC Y-up coordinates
    """
    translation, rotation, scale = blender_matrix.decompose()
    translation = convert_vector3(translation)
    rotation = convert_quaternion(rotation)

    mat_loc = Matrix.Translation(translation)
    mat_scale_1 = Matrix.Scale(scale[0], 4, (1, 0, 0))
    mat_scale_2 = Matrix.Scale(scale[2], 4, (0, 1, 0))
    mat_scale_3 = Matrix.Scale(scale[1], 4, (0, 0, 1))
    mat_scale = mat_scale_1 @ mat_scale_2 @ mat_scale_3
    mat_rot = rotation.to_matrix().to_4x4()

    return mat_loc @ mat_rot @ mat_scale
