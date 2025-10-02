from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from bpy.types import Context, Material


PROCEDURAL_NODE_TYPES = {
    'TEX_NOISE', 'TEX_GRADIENT', 'TEX_VORONOI', 'TEX_MAGIC',
    'TEX_WAVE', 'TEX_MUSGRAVE', 'TEX_CHECKER', 'TEX_BRICK'
}


def has_procedural_textures(material: Material) -> bool:
    """Check if material uses procedural texture nodes."""
    if not material.node_tree:
        return False

    for node in material.node_tree.nodes:
        if node.type in PROCEDURAL_NODE_TYPES:
            return True
    return False


def bake_material_textures(context: Context, material: Material, resolution: int = 1024) -> list[str]:
    """
    Bake procedural textures in material to image textures.

    Creates temporary objects, bakes textures, and replaces procedural nodes
    with Image Texture nodes pointing to baked images.

    Args:
        context: Blender context
        material: Material to bake
        resolution: Texture resolution (default 1024x1024)

    Returns:
        List of warning messages
    """
    warnings = []

    if not material.node_tree:
        warnings.append(f"Material '{material.name}' has no node tree")
        return warnings

    # Find material output node
    output_node = None
    for node in material.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL':
            output_node = node
            break

    if not output_node:
        warnings.append(f"Material '{material.name}' has no output node - skipping bake")
        return warnings

    # Check if material has surface input connected
    if not output_node.inputs['Surface'].is_linked:
        warnings.append(f"Material '{material.name}' has no surface shader connected - skipping bake")
        return warnings

    # Find procedural nodes
    procedural_nodes = [node for node in material.node_tree.nodes if node.type in PROCEDURAL_NODE_TYPES]
    if not procedural_nodes:
        return warnings

    # Create temporary baking object
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
    bake_obj = context.active_object
    bake_obj.name = f"__BAKE_TEMP_{material.name}"

    # Assign material to bake object
    if not bake_obj.data.materials:
        bake_obj.data.materials.append(material)
    else:
        bake_obj.data.materials[0] = material

    # Create UV map if needed
    if not bake_obj.data.uv_layers:
        bake_obj.data.uv_layers.new(name="UVMap")

    try:
        # Bake diffuse color
        baked_image = _bake_texture_channel(
            context, bake_obj, material, "DIFFUSE", resolution, warnings
        )

        if baked_image:
            # Replace procedural nodes with baked image texture
            _replace_procedural_with_baked(material, baked_image, output_node)
            warnings.append(f"Baked procedural textures for material '{material.name}' → '{baked_image.name}'")

    finally:
        # Clean up temporary object
        bpy.data.objects.remove(bake_obj, do_unlink=True)

    return warnings


def _bake_texture_channel(
    context: Context,
    bake_obj,
    material: Material,
    bake_type: str,
    resolution: int,
    warnings: list[str],
) -> bpy.types.Image | None:
    """
    Bake a specific texture channel.

    Args:
        context: Blender context
        bake_obj: Temporary object to bake onto
        material: Material being baked
        bake_type: Bake type ('DIFFUSE', 'NORMAL', etc.)
        resolution: Texture resolution
        warnings: List to append warnings to

    Returns:
        Baked image or None if baking failed
    """
    # Create image for baking
    image_name = f"{material.name}_baked_{bake_type.lower()}"
    baked_image = bpy.data.images.new(
        name=image_name,
        width=resolution,
        height=resolution,
        alpha=True,
        float_buffer=False,
    )

    # Create temporary image texture node for baking target
    nodes = material.node_tree.nodes
    temp_image_node = nodes.new('ShaderNodeTexImage')
    temp_image_node.name = "__BAKE_TARGET"
    temp_image_node.image = baked_image
    temp_image_node.select = True
    nodes.active = temp_image_node

    # Set render engine to Cycles for baking
    original_engine = context.scene.render.engine
    context.scene.render.engine = 'CYCLES'

    # Configure bake settings
    bake_settings = context.scene.cycles
    original_samples = bake_settings.samples
    bake_settings.samples = 32  # Lower samples for faster baking

    try:
        # Perform bake
        bpy.ops.object.bake(
            type=bake_type,
            pass_filter={'COLOR'},
            filepath='',
            width=resolution,
            height=resolution,
            margin=16,
            use_selected_to_active=False,
            use_clear=True,
        )

        # Pack the image to store in .blend file
        baked_image.pack()

        return baked_image

    except RuntimeError as e:
        warnings.append(f"Failed to bake material '{material.name}': {e}")
        bpy.data.images.remove(baked_image)
        return None

    finally:
        # Restore settings
        context.scene.render.engine = original_engine
        bake_settings.samples = original_samples

        # Remove temporary bake target node
        if temp_image_node:
            nodes.remove(temp_image_node)


def _replace_procedural_with_baked(material: Material, baked_image, output_node) -> None:
    """
    Replace procedural texture setup with baked image texture.

    Finds the shader connected to material output and replaces its
    Base Color input with the baked image texture.

    Args:
        material: Material to modify
        baked_image: Baked image to use
        output_node: Material output node
    """
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find the shader node connected to output
    surface_input = output_node.inputs['Surface']
    if not surface_input.is_linked:
        return

    shader_link = surface_input.links[0]
    shader_node = shader_link.from_node

    # Create new image texture node with baked image
    image_node = nodes.new('ShaderNodeTexImage')
    image_node.image = baked_image
    image_node.location = (shader_node.location.x - 300, shader_node.location.y)

    # Connect to shader's Base Color input (if it exists)
    if 'Base Color' in shader_node.inputs:
        # Disconnect existing Base Color connections
        base_color_input = shader_node.inputs['Base Color']
        for link in base_color_input.links:
            links.remove(link)

        # Connect baked image to Base Color
        links.new(image_node.outputs['Color'], base_color_input)


def bake_all_procedural_materials(context: Context, resolution: int = 1024) -> list[str]:
    """
    Bake all materials with procedural textures in the scene.

    Args:
        context: Blender context
        resolution: Bake resolution

    Returns:
        List of warnings/status messages
    """
    warnings = []
    materials_to_bake = []

    # Collect materials from scene objects only
    scene_materials = set()
    for obj in context.scene.objects:
        if obj.name.startswith("__"):
            continue
        if hasattr(obj, 'material_slots'):
            for slot in obj.material_slots:
                if slot.material and not slot.material.name.startswith("__"):
                    scene_materials.add(slot.material)

    # Find materials with procedural textures
    for material in scene_materials:
        if has_procedural_textures(material):
            materials_to_bake.append(material)

    if not materials_to_bake:
        warnings.append("No materials with procedural textures found")
        return warnings

    warnings.append(f"Baking {len(materials_to_bake)} material(s) at {resolution}x{resolution}...")

    for material in materials_to_bake:
        material_warnings = bake_material_textures(context, material, resolution)
        warnings.extend(material_warnings)

    return warnings
