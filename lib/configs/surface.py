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
        description="Name of the surface",
        default="Surface"
    )
    key: StringProperty(
        name="Key",
        description="prefix used to assign the surface to an object",
        default="ROAD"
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
        description="Wav file for the surface",
        default=""
    )
    wav_pitch: FloatProperty(
        name="Wav Pitch",
        description="Pitch of the wav file",
        default=1,
        min=0.5,
        max=2
    )
    ff_effect: StringProperty(
        name="FF Effect",
        description="Force Feedback Effect",
        default=""
    )
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
        description="Is this a pit lane surface",
        default=False
    )
    is_valid_track: BoolProperty(
        name="Is Valid Track",
        description="Is this a valid track surface",
        default=True
    )
    black_flag_time: IntProperty(
        name="Black Flag Time",
        description="Time before black flag is issued",
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
            "name": self.name,
            "key": self.key,
            "friction": self.friction,
            "damping": self.damping,
            "wav": self.wav,
            "wav_pitch": self.wav_pitch,
            "ff_effect": self.ff_effect,
            "dirt_additive": self.dirt_additive,
            "is_pit_lane": self.is_pit_lane,
            "is_valid_track": self.is_valid_track,
            "black_flag_time": self.black_flag_time,
            "sin_height": self.sin_height,
            "sin_length": self.sin_length,
            "vibration_gain": self.vibration_gain,
            "vibration_length": self.vibration_length
        }

    # long floats may be interpreted as strings when reading from file
    # so we should cast non-string types to prevent errors
    def from_dict(self, data: dict):
        self.name = data["name"]
        self.key = data["key"]
        if data["key"] in ['ROAD', 'KERB', 'GRASS', 'SAND']:
            self.custom = False
            return
        self.custom = True
        self.friction = float(data["friction"])
        self.damping = float(data["damping"])
        self.wav = data["wav"]
        self.wav_pitch = float(data["wav_pitch"])
        self.ff_effect = data["ff_effect"]
        self.dirt_additive = float(data["dirt_additive"])
        self.is_pit_lane = bool(data["is_pit_lane"])
        self.is_valid_track = bool(data["is_valid_track"])
        self.black_flag_time = int(data["black_flag_time"])
        self.sin_height = float(data["sin_height"])
        self.sin_length = float(data["sin_length"])
        self.vibration_gain = float(data["vibration_gain"])
        self.vibration_length = float(data["vibration_length"])
