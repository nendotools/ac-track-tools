###
#  This file contains helper properties not available natively in the Blender API.
###
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, CollectionProperty

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
