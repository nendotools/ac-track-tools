"""Texture node PropertyGroup for KN5 export."""

from bpy.props import StringProperty
from bpy.types import PropertyGroup


class AC_TextureSettings(PropertyGroup):
    """Assetto Corsa texture node settings for KN5 export."""

    shader_input_name: StringProperty(
        name="Shader Input",
        description="AC shader texture slot (txDiffuse, txNormal, txDetail, etc.)",
        default="txDiffuse",
    )
