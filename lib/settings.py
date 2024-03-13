import re
import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import CollectionProperty, PointerProperty, StringProperty

from .configs.track import AC_Track
from .configs.surface import AC_Surface
from .configs.audio_source import AC_AudioSource

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
    audio_sources: CollectionProperty(
        type=AC_AudioSource,
        name="Audio Sources",
    )
    error: dict = {}
    active_surfaces: list[str] = []
    default_surfaces: dict = {
        "ROAD": {
            "KEY": "ROAD",
            "NAME": "Road",
            "FRICTION": 1,
        },
        "KERB": {
            "KEY": "KERB",
            "NAME": "Kerb",
            "FRICTION": 0.92,
            "WAV": "kerb.wav",
            "WAV_PITCH": 1.3,
            "FF_EFFECT": 1,
            "VIBRATION_GAIN": 1.0,
            "VIBRATION_LENGTH": 1.5,
        },
        "GRASS": {
            "KEY": "GRASS",
            "NAME": "Grass",
            "FRICTION": 0.6,
            "WAV": "grass.wav",
            "WAV_PITCH": 0,
            "DIRT_ADDITIVE": 1,
            "IS_VALID_TRACK": False,
            "sin_height": 0.03,
            "SIN_LENGTH": 0.5,
            "VIBRATION_GAIN": 0.2,
            "VIBRATION_LENGTH": 0.6,
        },
        "SAND": {
            "KEY": "SAND",
            "NAME": "Sand",
            "FRICTION": 0.8,
            "DAMPING": 0.1,
            "WAV": "sand.wav",
            "WAV_PITCH": 0,
            "FF_EFFECT": 0,
            "DIRT_ADDITIVE": 1,
            "IS_VALID_TRACK": False,
            "SIN_HEIGHT": 0.04,
            "SIN_LENGTH": 0.5,
            "VIBRATION_GAIN": 0.2,
            "VIBRATION_LENGTH": 0.3,
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

    def map_audio(self) -> dict:
        audio_map = {}
        for audio in self.audio_sources:
            mapped = audio.to_dict()
            audio_map[mapped['NAME']] = mapped
            audio_map[mapped['NAME']].pop('NAME')
        return audio_map

    def load_audio(self, audio_map: dict):
        self.audio_sources.clear()
        for audio in audio_map.items():
            if audio[0].startswith("DEFAULT"):
                continue
            if not audio[0]:
                continue
            new_audio = self.audio_sources.add()
            audio[1]['NAME'] = audio[0]
            new_audio.from_dict(audio[1])
            # find the object in the scene by name and assign it to the audio source
            new_audio.node_pointer = bpy.data.objects.get(audio[1]["NODE"])

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
