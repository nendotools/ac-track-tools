from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty

class AC_Surface(PropertyGroup):
    custom: BoolProperty(
        name="Custom",
        description="Is this a custom surface",
        default=True
    )
    name: StringProperty(
        name="Name",
        description="Standard name of the surface",
        default="Track Surface"
    )
    key: StringProperty(
        name="Key",
        description="Unique prefix used to assign the surface to an object",
        default="SURFACE"
    )
    friction: FloatProperty(
        name="Friction",
        description="dry surface grip (slip <--------> grip)",
        default=0.96,
        min=0,
        max=1,
        precision=2
    )
    damping: FloatProperty(
        name="Damping",
        description="speed reduction on the surface (road <-------> sand)",
        default=0,
        min=0,
        max=1,
        precision=2
    )
    wav: StringProperty(
        name="Wav",
        description="Wav file to play while driving on the surface",
        default=""
    )
    wav_pitch: FloatProperty(
        name="Wav Pitch",
        description="Pitch shift of the wav file",
        default=1,
        min=0.5,
        max=2
    )
    ff_effect: StringProperty(
        name="FF Effect",
        description="Force Feedback Effect [optional]",
        default="",
        update=lambda s, c: s.update_ff_effect(c)
    )
    def update_ff_effect(self, context):
        if self.ff_effect == 'NULL':
            self.ff_effect = ''

    dirt_additive: FloatProperty(
        name="Dirt Additive",
        description="Amount of dirt added from the surface",
        default=0,
        min=0,
        max=0.45,
        precision=2
    )
    is_pit_lane: BoolProperty(
        name="Is Pit Lane",
        description="Apply Pit Lane rules to surface?",
        default=False
    )
    is_valid_track: BoolProperty(
        name="Is Valid Track",
        description="Is this surface part of the track?",
        default=True
    )
    black_flag_time: IntProperty(
        name="Black Flag Time",
        description="Seconds on surface before black flag is issued",
        default=0,
        min=0,
        max=60,
        step=5
    )
    sin_height: FloatProperty(
        name="Sin Height",
        description="Height of the sin wave",
        default=0,
        min=0,
        max=3,
        precision=2
    )
    sin_length: FloatProperty(
        name="Sin Length",
        description="Length of the sin wave",
        default=0,
        min=0,
        max=3,
        precision=2
    )
    vibration_gain: FloatProperty(
        name="Vibration Gain",
        description="Gain of the vibration",
        default=0,
        min=0,
        max=3,
        precision=2
    )
    vibration_length: FloatProperty(
        name="Vibration Length",
        description="Length of the vibration",
        default=0,
        min=0,
        max=3,
        precision=2
    )

    def to_dict(self) -> dict:
        return {
            "NAME": self.name,
            "KEY": self.key,
            "FRICTION": self.friction,
            "DAMPING": self.damping,
            "WAV": self.wav,
            "WAV_PITCH": self.wav_pitch,
            "FF_EFFECT": 'NULL' if self.ff_effect == '' else self.ff_effect,
            "DIRT_ADDITIVE": self.dirt_additive,
            "IS_PITLANE": self.is_pit_lane,
            "IS_VALID_TRACK": self.is_valid_track,
            "BLACK_FLAG_TIME": self.black_flag_time,
            "SIN_HEIGHT": self.sin_height,
            "SIN_LENGTH": self.sin_length,
            "VIBRATION_GAIN": self.vibration_gain,
            "VIBRATION_LENGTH": self.vibration_length,
        }

    # long floats may be interpreted as strings when reading from file
    # so we should cast non-string types to prevent errors
    def from_dict(self, data: dict, custom: bool = True):
        self.name = data["NAME"] if "NAME" in data else data["KEY"]
        self.key = data["KEY"]
        self.custom = custom
        self.friction = float(data["FRICTION"]) if "FRICTION" in data else 0.99
        self.damping = float(data["DAMPING"]) if "DAMPING" in data else 0
        self.wav = data["WAV"] if "WAV" in data else ""
        self.wav_pitch = float(data["WAV_PITCH"]) if "WAV_PITCH" in data else 1
        self.ff_effect = f'{data["FF_EFFECT"]}' if "FF_EFFECT" in data else ""
        self.dirt_additive = float(data["DIRT_ADDITIVE"]) if "DIRT_ADDITIVE" in data else 0
        self.is_pit_lane = bool(data["IS_PITLANE"]) if "IS_PITLANE" in data else False
        self.is_valid_track = bool(data["IS_VALID_TRACK"]) if "IS_VALID_TRACK" in data else True
        self.black_flag_time = int(data["BLACK_FLAG_TIME"]) if "BLACK_FLAG_TIME" in data else 0
        self.sin_height = float(data["SIN_HEIGHT"]) if "SIN_HEIGHT" in data else 0
        self.sin_length = float(data["SIN_LENGTH"]) if "SIN_LENGTH" in data else 0
        self.vibration_gain = float(data["VIBRATION_GAIN"]) if "VIBRATION_GAIN" in data else 0
        self.vibration_length = float(data["VIBRATION_LENGTH"]) if "VIBRATION_LENGTH" in data else 0
