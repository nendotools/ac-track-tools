import bpy

menu_state = {
    "active_menu": "SURFACES"
}

class AC_UISettings(bpy.types.PropertyGroup):
    menu: bpy.props.EnumProperty(
        name="Menu",
        description="Currently Selected Menu",
        default="SURFACES",
        items=[
            ("SURFACES", "Surfaces", "Create and manage surfaces"),
            ("ASSETS", "Assets", "Create and manage assets"),
            ("NODES", "Nodes", "Create and manage nodes"),
            ("SOUNDS", "Sounds", "Create and manage sounds"),
            ("CAMERAS", "Cameras", "Create and manage cameras"),
            ("LIGHTING", "Lighting", "Create and manage lighting"),
            ("SETTINGS", "Settings", "Create and manage settings"),
        ],
    )

