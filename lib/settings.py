import re
import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import CollectionProperty, PointerProperty, StringProperty

from .configs.surface import AC_Surface
from .configs.track import AC_Track

class AC_Settings(PropertyGroup):
    working_dir: StringProperty(
        name="Working Directory",
        description="Directory to save and load files",
        default="",
        subtype='DIR_PATH',
        update=lambda self, context: self.update_directory(self.working_dir),
    )
    initialized: bool = False # check if the folder structure has been initialized
    track: PointerProperty(
        type=AC_Track,
        name="Track",
    )
    surfaces: CollectionProperty(
        type=AC_Surface,
        name="Track Surfaces",
    )
    error: dict = {}
    active_surfaces: list[str] = []
    default_surfaces: dict = {
        "ROAD": {
            "key": "ROAD",
            "name": "Road",
        },
        "KERB": {
            "key": "KERB",
            "name": "Kerb",
        },
        "GRASS": {
            "key": "GRASS",
            "name": "Grass",
        },
        "SAND": {
            "key": "SAND",
            "name": "Sand",
        },
    }

    def reset_errors(self):
        self.error.clear()

    def get_surface_groups(self, context, key: str | None = None) -> list[Object] | dict[str, Object]:
        # dict of lists surface keys
        groups = {}
        for surface in self.surfaces:
            if surface.key not in groups:
                groups[surface.key] = []

        # if key is provided, only return objects from the scene matching the key
        for surfaceKey in groups:
            objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
            for obj in objects:
                match = re.match(rf"^\d*{surfaceKey}.*$", obj.name)
                if match:
                    groups[surfaceKey].append(obj)

        return groups if key is None else groups[key]

    def update_directory(self, path: str):
        if path == "":
            return
        self.initialized = True
        print("initializing directory", path)
        bpy.ops.ac.load_settings()

    def map_surfaces(self) -> dict:
        surface_map = {}
        keys = ['ROAD', 'KERB', 'GRASS', 'SAND']

        # only save custom surfaces
        custom_surfaces = [surface for surface in self.surfaces if surface.custom]
        for i, surface in enumerate(custom_surfaces):
            # validity check
            if not re.match(r"^[A-Z]*$", surface.key):
                self.error["surface"] = f"Surface {surface.name} assigned invalid key: {surface.key}"

            # duplicate check
            if surface.key in keys:
                self.error["surface"] = f"Surface {surface.name} assigned duplicate key: {surface.key}"

            keys.append(surface.key)
            surface_map[f"SURFACE_{i}"] = surface.to_dict()
        return surface_map

    def load_surfaces(self, surface_map: dict):
        self.surfaces.clear()
        for surface in {**self.default_surfaces, **surface_map}.items():
            if surface[0].startswith("DEFAULT"):
                continue
            new_surface = self.surfaces.add()
            new_surface.from_dict(surface[1])

    def map_track(self) -> dict:
        return self.track.to_dict()

    def load_track(self, track: dict):
        self.track.from_dict(track)


def get_settings() -> AC_Settings:
    return bpy.context.scene.AC_Settings # type: ignore
