"""
Shader default configurations for Assetto Corsa materials.

Each shader has specific material properties and texture requirements.
"""

SHADER_DEFAULTS = {
    "ksPerPixel": {
        "description": "Standard per-pixel shader for most objects",
        "properties": [
            {"name": "ksDiffuse", "valueA": 0.4},
            {"name": "ksAmbient", "valueA": 0.4},
        ],
        "required_textures": ["txDiffuse"],
        "optional_textures": [],
        "alpha_tested": False,
        "alpha_blend_mode": 0,  # Opaque
        "depth_mode": 0,  # DepthNormal
    },
    "ksTree": {
        "description": "Tree shader with auto-normals for natural lighting",
        "properties": [
            {"name": "ksDiffuse", "valueA": 0.25},
            {"name": "ksAmbient", "valueA": 0.3},
            {"name": "ksSpecular", "valueA": 0.0},
        ],
        "required_textures": ["txDiffuse"],
        "optional_textures": [],
        "alpha_tested": True,
        "alpha_blend_mode": 0,  # Opaque
        "depth_mode": 0,
        "naming_prefix": "KSTREE_GROUP_",
        "special_requirements": [
            "Object origin must be at bottom of mesh",
            "Normals should be set vertically",
            "Use continuous numbering (e.g. KSTREE_GROUP_oak_1, KSTREE_GROUP_oak_2)",
        ],
    },
    "ksGrass": {
        "description": "Grass shader with variation texture support",
        "properties": [
            {"name": "ksDiffuse", "valueA": 0.4},
            {"name": "ksAmbient", "valueA": 0.4},
        ],
        "required_textures": ["txDiffuse", "txVariation"],
        "optional_textures": [],
        "alpha_tested": True,
        "alpha_blend_mode": 0,
        "depth_mode": 0,
    },
    "ksPerPixelMultiMap": {
        "description": "Per-pixel shader with normal, specular, and detail maps",
        "properties": [
            {"name": "ksDiffuse", "valueA": 0.4},
            {"name": "ksAmbient", "valueA": 0.4},
            {"name": "ksSpecular", "valueA": 0.2},
            {"name": "ksSpecularEXP", "valueA": 50.0},
        ],
        "required_textures": ["txDiffuse"],
        "optional_textures": ["txNormal", "txMaps", "txDetail"],
        "alpha_tested": False,
        "alpha_blend_mode": 0,
        "depth_mode": 0,
    },
    "ksMultilayer": {
        "description": "Multi-layer shader with mask and detail textures",
        "properties": [
            {"name": "ksDiffuse", "valueA": 0.4},
            {"name": "ksAmbient", "valueA": 0.4},
        ],
        "required_textures": ["txDiffuse", "txMask"],
        "optional_textures": ["txDetailR", "txDetailG", "txDetailB", "txDetailA"],
        "alpha_tested": False,
        "alpha_blend_mode": 0,
        "depth_mode": 0,
    },
}


def get_shader_list(self, context):
    """Get list of available shaders for EnumProperty."""
    return [(name, name, defaults.get("description", "")) for name, defaults in SHADER_DEFAULTS.items()]


def get_shader_defaults(shader_name: str) -> dict:
    """Get default configuration for a shader."""
    return SHADER_DEFAULTS.get(shader_name, SHADER_DEFAULTS["ksPerPixel"])


def get_required_textures(shader_name: str) -> list[str]:
    """Get list of required textures for a shader."""
    defaults = get_shader_defaults(shader_name)
    return defaults.get("required_textures", [])


def get_optional_textures(shader_name: str) -> list[str]:
    """Get list of optional textures for a shader."""
    defaults = get_shader_defaults(shader_name)
    return defaults.get("optional_textures", [])
