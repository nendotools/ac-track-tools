import re

import bpy
from bpy.props import CollectionProperty, PointerProperty, StringProperty
from bpy.types import Object, PropertyGroup

from ..utils.files import find_maps, get_active_directory, set_path_reference
from ..utils.properties import ExtensionCollection
from .configs.audio_source import AC_AudioSource
from .configs.lighting import AC_Lighting
from .configs.surface import AC_Surface
from .configs.track import AC_Track


class AC_Settings(PropertyGroup):
    working_dir: StringProperty(
        name="Working Directory",
        description="Directory to save and load files",
        default="",
        subtype='DIR_PATH',
        update=lambda s, _: s.update_directory(s.working_dir),
    )
    track: PointerProperty(
        type=AC_Track,
        name="Track",
    )
    surfaces: CollectionProperty(
        type=AC_Surface,
        name="Track Surfaces",
    )
    surface_ext: CollectionProperty(
        type=ExtensionCollection,
        name="Surface Extensions",
        description="Unsupported extension to save/load",
    )
    global_extensions: CollectionProperty(
        type=ExtensionCollection,
        name="Global Extensions",
        description="Unsupported extension to save/load"
    )
    audio_sources: CollectionProperty(
        type=AC_AudioSource,
        name="Audio Sources",
    )
    lighting: PointerProperty(
        type=AC_Lighting,
        name="Lighting",
    )
    error: list[dict] = []
    surface_errors: dict = {}
    active_surfaces: list[str] = []
    default_surfaces: dict = {
        "SURFACE_ROAD": {
            "KEY": "ROAD",
            "NAME": "Road",
            "FRICTION": 1,
            "CUSTOM": False
        },
        "SURFACE_KERB": {
            "KEY": "KERB",
            "NAME": "Kerb",
            "FRICTION": 0.92,
            "WAV": "kerb.wav",
            "WAV_PITCH": 1.3,
            "FF_EFFECT": 1,
            "VIBRATION_GAIN": 1.0,
            "VIBRATION_LENGTH": 1.5,
            "CUSTOM": False
        },
        "SURFACE_GRASS": {
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
            "CUSTOM": False
        },
        "SURFACE_SAND": {
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
            "CUSTOM": False
        },
    }

    def reset_errors(self):
        self.error.clear()

    def get_surface_groups(self, context, key: str | None = None, ex_key: str | None = None) -> list[Object] | dict[str, Object]:
        # dict of lists surface keys
        groups = {}
        for surface in self.surfaces:
            if surface.key not in groups:
                groups[surface.key] = []
        groups['WALL'] = []

        # if key is provided, only return objects from the scene matching the key
        for surfaceKey in groups:
            objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
            for obj in objects:
                match = re.match(rf"^\d*{surfaceKey}.*$", obj.name)
                if match:
                    groups[surfaceKey].append(obj)

        if key:
            return groups[key]
        if ex_key:
            groups.pop(ex_key)
            return [obj for sublist in groups.values() for obj in sublist]
        return groups

    def get_walls(self, context) -> list[Object]:
        return self.get_surface_groups(context, "WALL") # type: ignore

    def get_nonwalls(self, context) -> list[Object]:
        return self.get_surface_groups(context, ex_key="WALL") # type: ignore

    def check_copy_names(self, context) -> bool:
        # detect any AC objects with names ending in .001, .002, etc.
        obs = [obj for obj in context.scene.objects if obj.name.startswith("AC_")]
        for ob in obs:
            if re.match(rf".*\.\d+$", ob.name):
                return True
        return False

    # return a list of {severity: int, message: str} objects
    # severity: 0 = info, 1 = warning (fixable), 2 = error (unfixable)
    def run_preflight(self, context) -> list:
        self.error.clear()
        if not context.preferences.addons['io_scene_fbx']:
            self.error.append({
                "severity": 2,
                "message": "FBX Exporter not enabled",
                "code": "NO_FBX"
            })
        if len(self.get_pitboxes(context)) != len(self.get_starts(context)):
            self.error.append({
                "severity": 2,
                "message": "Pitbox <-> Race Start mismatch",
                "code": "PITBOX_START_MISMATCH"
            })
        if len(self.get_pitboxes(context)) != self.track.pitboxes:
            self.error.append({
                "severity": 1,
                "message": "Pitbox count mismatch",
                "code": "PITBOX_COUNT_MISMATCH"
            })
        if not self.get_nonwalls(context):
            self.error.append({
            "severity": 2,
            "message": "No track surfaces assigned",
            "code": "NO_SURFACES"
            })
        if not self.get_walls(context):
            self.error.append({
                "severity": 0,
                "message": "No walls assigned",
                "code": "NO_WALLS"
            })
        if self.check_copy_names(context):
            self.error.append({
                "severity": 1,
                "message": "Track object index errors detected",
                "code": "DUPLICATE_NAMES"
            })
        if context.scene.unit_settings.system != 'METRIC':
            self.error.append({
            "severity": 1,
            "message": "Scene units are not set to Metric",
            "code": "IMPERIAL_UNITS"
            })
        if context.scene.unit_settings.length_unit != 'METERS':
            self.error.append({
            "severity": 1,
            "message": "Scene units are not set to Meters",
            "code": "INVALID_UNITS"
            })
        if context.scene.unit_settings.scale_length != 1:
            self.error.append({
            "severity": 1,
            "message": "Scene scale is not set to 1",
            "code": "INVALID_UNIT_SCALE"
            })
        # - fbx export settings wrong
        # - objects are not assigned materials
        # - check for missing material textures not in texture folder
        # - check for missing map files
        if not self.working_dir or self.working_dir == "":
            return self.error
        if self.working_dir != get_active_directory():
            set_path_reference(self.working_dir)
        map_files = find_maps()
        if not map_files['map']:
            self.error.append({
            "severity": 2,
            "message": 'No map file found "./map.png"',
            "code": "NO_MAP"
            })
        if not map_files['outline']:
            self.error.append({
            "severity": 2,
            "message": 'No outline file found "./ui/outline.png"',
            "code": "NO_OUTLINE"
            })
        if not map_files['preview']:
            self.error.append({
            "severity": 2,
            "message": 'No preview file found "./ui/preview.png"',
            "code": "NO_PREVIEW"
            })
        
        return self.error


    def update_directory(self, path: str):
        if path == "":
            return
        set_path_reference(path)
        bpy.ops.ac.load_settings()

    def get_surfaces(self) -> list[AC_Surface]:
        out_surfaces = {}
        for surface in self.surfaces:
            out_surfaces[surface.key] = surface
        return list(out_surfaces.values())

    def map_surfaces(self) -> dict:
        surface_map = {}

        # only save custom surfaces
        custom_surfaces = [surface for surface in self.surfaces if surface.custom]
        for i, surface in enumerate(custom_surfaces):
            # validity check
            if not re.match(r"^[A-Z]*$", surface.key):
                self.surface_errors["surface"] = f"Surface {surface.name} assigned invalid key: {surface.key}"

            surface_map[f"SURFACE_{i}"] = surface.to_dict()

        for extension in self.surface_ext:
            surface_map[extension.name] = {}
            for item in extension.items:
                surface_map[extension.name][item.key] = item.value
        return surface_map

    def load_surfaces(self, surface_map: dict):
        self.surfaces.clear()
        self.surface_ext.clear()
        for surface in {**self.default_surfaces, **surface_map}.items():
            if surface[0].startswith("DEFAULT"):
                continue
            if not surface[0].startswith("SURFACE_"):
                extension = self.surface_ext.add()
                extension.name = surface[0]
                for key, value in surface[1].items():
                    pair = extension.items.add()
                    pair.key = key
                    pair.value = f"{value}"
                continue
            new_surface = self.surfaces.add()
            new_surface.from_dict(surface[1], surface[1]["CUSTOM"] if "CUSTOM" in surface[1] else True)

    def map_track(self, context) -> dict:
        track_info = self.track.to_dict()
        track_info.update({
            "pitboxes": len(self.get_pitboxes(context)),
        })
        return track_info

    def load_track(self, track: dict):
        self.track.from_dict(track)

    def map_lighting(self) -> dict:
        return self.lighting.to_dict()

    def load_lighting(self, lighting: dict):
        for section in lighting.items():
            if section[0] == "DEFAULT":
                continue
            self.lighting.from_dict(section[1])

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
            pointer_name = audio[1]["NODE"] if "NODE" in audio[1] else audio[1]["NAME"]
            # find the object in the scene by name and assign it to the audio source
            new_audio.node_pointer = bpy.data.objects.get(pointer_name)

    # extensions are stored in a single config file, but should be organized by group within the UI.
    # each config section should get mapped to the proper config group when loaded, then saved back to the same file
    def map_extensions(self) -> dict:
        extension_map = {}
        for extension in self.global_extensions:
            extension_map[extension.name] = {}
            for item in extension.items:
                extension_map[extension.name][item.key] = item.value

        extension_map["LIGHTING"] = self.lighting.global_lighting.to_dict()
        return extension_map

    def load_extensions(self, extension_map: dict):
        for extension in extension_map.items():
            if extension[0].startswith("DEFAULT") or not extension[0]:
                continue

            if extension[0] == "LIGHTING": #global light settings
                self.lighting.global_lighting.from_dict(extension[1])
                continue

            elif extension[0].startswith("LIGHT_"): # individual lighting: using elif to avoid double assignment
                # self.lighting.light_from_dict(extension[1], True if extension[0].startswith("LIGHT_SERIES_") else False)
                # continue
                pass

            ext_group = self.global_extensions.add()
            ext_group.name = extension[0]
            for item in extension[1].items():
                new_item = ext_group.items.add()
                new_item.key = item[0]
                new_item.value = item[1]

    def get_starts(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_START")]

    def get_pitboxes(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_PIT")]

    def get_hotlap_starts(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_HOTLAP_START")]

    def get_time_gates(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_TIME")]

    def get_ab_start_gates(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_AB_START")]

    def get_ab_finish_gates(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_AB_FINISH")]

    def get_audio_emitters(self, context) -> list[Object]:
        return [obj for obj in context.scene.objects if obj.name.startswith("AC_AUDIO")]

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
