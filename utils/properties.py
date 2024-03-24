###
#  This file contains helper properties not available natively in the Blender API.
###
from bpy.props import (BoolProperty, CollectionProperty, IntProperty,
                       StringProperty)
from bpy.types import PropertyGroup


class KeyValuePair(PropertyGroup):
    key: StringProperty(
        name="Key",
        description="Key",
        default="KEY"
    )
    value: StringProperty(
        name="Value",
        description="Value",
        default="value"
    )

class ExtensionCollection(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="Section Name for the collection",
        default="_EXT"
    )
    expand: BoolProperty(
        name="Expand",
        description="Expand the audio source properties",
        default=False
    )
    items: CollectionProperty(
        type=KeyValuePair,
        name="Items",
        description="Items for the collection",
    )
    index: IntProperty(
        name="Index",
        description="Index of the items",
        default=-1
    )
