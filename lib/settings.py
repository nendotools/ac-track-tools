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
            "friction": 1,
        },
        "KERB": {
            "key": "KERB",
            "name": "Kerb",
            "friction": 0.92,
            "wav": "kerb.wav",
            "wav_pitch": 1.3,
            "ff_effect": 1,
            "vibration_gain": 1.0,
            "vibration_length": 1.5,
        },
        "GRASS": {
            "key": "GRASS",
            "name": "Grass",
            "friction": 0.6,
            "wav": "grass.wav",
            "wav_pitch": 0,
            "dirt_additive": 1,
            "is_valid_track": False,
            "sin_height": 0.03,
            "sin_length": 0.5,
            "vibration_gain": 0.2,
            "vibration_length": 0.6,
        },
        "SAND": {
            "key": "SAND",
            "name": "Sand",
            "friction": 0.8,
            "damping": 0.1,
            "wav": "sand.wav",
            "wav_pitch": 0,
            "ff_effect": 0,
            "dirt_additive": 1,
            "is_valid_track": False,
            "sin_height": 0.04,
            "sin_length": 0.5,
            "vibration_gain": 0.2,
            "vibration_length": 0.3,
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
        print("updating directory:", path)
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

    def get_starts(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_START")]

    def get_pitboxes(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_PITBOX")]

    def get_hotlap_starts(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_HOTLAP_START")]

    def get_time_gates(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_TIME")]

    def get_ab_start_gates(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_AB_START")]

    def get_ab_finish_gates(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_AB_FINISH")]

    def consolidate_logic_gates(self, context):
        starts = self.get_starts(context)
        hotlap_starts = self.get_hotlap_starts(context)
        time_gates = self.get_time_gates(context)
        pitboxes = self.get_pitboxes(context)

        for i, gate in enumerate(starts):
            gate.name = f"AC_START_{i}"
        for i, gate in enumerate(hotlap_starts):
            gate.name = f"AC_HOTLAP_START_{i}"
        l_times = [gate for gate in time_gates if gate.name.endswith("_L")]
        r_times = [gate for gate in time_gates if gate.name.endswith("_R")]
        for i, gate in enumerate(l_times):
            gate.name = f"AC_TIME_{i}_L"
        for i, gate in enumerate(r_times):
            gate.name = f"AC_TIME_{i}_R"
        for i, box in enumerate(pitboxes):
            box.name = f"AC_PIT_{i}"


def get_settings() -> AC_Settings:
    return bpy.context.scene.AC_Settings # type: ignore
