from bpy.types import PropertyGroup
from bpy.props import IntProperty

class AC_Lighting(PropertyGroup):
    sun_pitch_angle: IntProperty(
        name="Sun Pitch Angle",
        description="The pitch angle of the sun (sunrise <-> noon)",
        default=45,
        min=0,
        max=180
    )

    sun_heading_angle: IntProperty(
        name="Sun Heading Angle",
        description="The heading angle of the sun (cardinal direction)",
        default=0,
        min=-180,
        max=180
    )
