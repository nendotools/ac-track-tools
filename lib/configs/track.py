import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    StringProperty,
    FloatProperty,
    EnumProperty,
    IntProperty,
    BoolProperty
)
from ...utils.properties import KeyValuePair

run_modes = [
    ("A2B", "a-b", "A to B"),
    ("B2A", "b-a", "B to A"),
    ("CW", "clockwise", "Clockwise"),
    ("CCW", "counter-clockwise", "Counter Clockwise")
]

# TODO: handle tags and geotags as a list of strings
class AC_Track(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="Name of the track",
        default=""
    )
    description: StringProperty(
        name="Description",
        description="Description of the track",
        default=""
    )
    tags: CollectionProperty(
        type=KeyValuePair,
        name="Tags",
        description="Tags for the track",
    )
    show_tags: BoolProperty(
        name="Show Tags",
        description="Show the tags in the UI",
        default=True
    )
    tags_index: IntProperty(
        name="Tags Index",
        description="Index of the tags",
        default=-1
    )
    geotags: CollectionProperty(
        type=KeyValuePair,
        name="GeoTags",
        description="GeoTags for the track",
    )
    show_geotags: BoolProperty(
        name="Show GeoTags",
        description="Show the geotags in the UI",
        default=True
    )
    geotags_index: IntProperty(
        name="GeoTags Index",
        description="Index of the geotags",
        default=-1
    )
    country: StringProperty(
        name="Country",
        description="Country of the track",
        default=""
    )
    city: StringProperty(
        name="City",
        description="City of the track",
        default=""
    )
    length: StringProperty(
        name="Length",
        description="Length of the track",
        default="0m"
    )
    width: StringProperty(
        name="Width",
        description="Width of the track",
        default="0m",
    )
    # I've found that some tracks use custom values for run, but it's not worth it to account for all possibilities
    # as they all tend to be some derivative of a-b (drag, sprint, hill-climb, etc) or clockwise (circuit, rally, etc).
    # Those specifics are better off declared in tags for searchability.
    run: EnumProperty(
        name="Run",
        items=run_modes,
        description="Run direction",
        default="CW"
    )

    # may not be needed as we can automate it by detecting the named objects
    pitboxes: IntProperty(
        name="Pitboxes",
        description="Number of pitboxes",
        default=0,
        min=0
    )

    # image outline reference
    # should capture an overhead view with only the track objects visible in white
    outline: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Outline",
        description="Outline of the track"
    )

    # should capture a render from a camera in the scene
    preview: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Preview",
        description="Preview shot of the track scenery"
    )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "tags": [item.value for item in self.tags],
            "geotags": [item.value for item in self.geotags],
            "country": self.country,
            "city": self.city,
            "length": self.length,
            "width": self.width,
            "run": self.get_run_mode_value(self.run),
            "pitboxes": self.pitboxes
        }

    def get_run_mode_key(self, mode: str) -> str:
        for item in run_modes:
            if item[1] == mode:
                return item[0]
        return "CW"

    def get_run_mode_value(self, key: str) -> str:
        for item in run_modes:
            if item[0] == key:
                return item[1]
        return "clockwise"

    def from_dict(self, data: dict):
        self.name = data["name"]
        self.description = data["description"]
        self.tags.clear()
        for value in data["tags"]:
            item = self.tags.add()
            item.value = value
        self.geotags.clear()
        for value in data["geotags"]:
            item = self.geotags.add()
            item.value = value
        self.country = data["country"]
        self.city = data["city"]
        self.length = data["length"]
        self.width = data["width"]
        self.run = self.get_run_mode_key(data['run']) if data["run"] in ["a-b", "b-a", "clockwise", "counter clockwise"] else "CW"
        self.pitboxes = int(data["pitboxes"])
