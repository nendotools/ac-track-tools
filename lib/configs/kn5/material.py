"""Material PropertyGroups for KN5 export."""

from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
                       FloatProperty, FloatVectorProperty, IntProperty,
                       StringProperty)
from bpy.types import PropertyGroup

from ...kn5.shader_defaults import get_shader_list


class AC_ShaderProperty(PropertyGroup):
    """Shader property with up to 4 component values."""

    name: StringProperty(
        name="Property Name",
        description="Shader property name (e.g., ksDiffuse, ksAmbient)",
        default="ksDiffuse",
    )
    valueA: FloatProperty(
        name="Value A",
        description="Single float value",
        default=0.0,
    )
    valueB: FloatVectorProperty(
        name="Value B",
        description="2-component vector",
        size=2,
        default=(0.0, 0.0),
    )
    valueC: FloatVectorProperty(
        name="Value C",
        description="3-component vector (RGB or XYZ)",
        size=3,
        default=(0.0, 0.0, 0.0),
    )
    valueD: FloatVectorProperty(
        name="Value D",
        description="4-component vector (RGBA or XYZW)",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
    )


class AC_MaterialSettings(PropertyGroup):
    """Assetto Corsa material settings for KN5 export."""

    shader_name: EnumProperty(
        name="Shader",
        description="AC shader to use for this material",
        items=get_shader_list,
        default=0,
    )
    alpha_blend_mode: EnumProperty(
        name="Alpha Blend Mode",
        description="How to handle alpha blending",
        items=[
            ("0", "Opaque", "No transparency"),
            ("1", "Alpha Blend", "Standard alpha blending"),
            ("2", "Alpha to Coverage", "MSAA-based transparency"),
        ],
        default="0",
    )
    alpha_tested: BoolProperty(
        name="Alpha Tested",
        description="Enable alpha testing (cutout transparency)",
        default=False,
    )
    depth_mode: EnumProperty(
        name="Depth Mode",
        description="Depth buffer write mode",
        items=[
            ("0", "Depth Normal", "Normal depth writing"),
            ("1", "Depth No Write", "Read depth but don't write"),
            ("2", "Depth Off", "No depth testing"),
        ],
        default="0",
    )
    shader_properties: CollectionProperty(
        type=AC_ShaderProperty,
        name="Shader Properties",
        description="Material shader properties (ksDiffuse, ksAmbient, etc.)",
    )
    shader_properties_active: IntProperty(
        name="Active Shader Property",
        description="Active property in the list",
        default=-1,
    )
