###
#  This file contains helper properties not available natively in the Blender API.
###
from bpy.types import PropertyGroup
from bpy.props import StringProperty

class KeyValuePair(PropertyGroup):
    key: StringProperty(
        name="Key",
        description="Key",
        default=""
    )
    value: StringProperty(
        name="Value",
        description="Value",
        default=""
    )
