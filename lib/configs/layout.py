import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup
import json


class AC_LayoutCollection(PropertyGroup):
    """Maps a Blender collection to a layout"""

    collection_name: StringProperty(
        name="Collection Name",
        description="Name of the Blender collection"
    )

    enabled: BoolProperty(
        name="Enabled",
        description="Include this collection/KN5 in the layout",
        default=True
    )

    def to_dict(self) -> dict:
        return {
            "collection": self.collection_name,
            "enabled": self.enabled
        }

    def from_dict(self, data: dict):
        self.collection_name = data.get("collection", "")
        self.enabled = data.get("enabled", True)


class AC_TrackLayout(PropertyGroup):
    """Represents a track layout/variant"""

    name: StringProperty(
        name="Layout Name",
        description="Layout identifier (e.g., 'club', 'national')",
        default="layout",
        maxlen=15  # AC limit for layout folder names
    )

    collections: CollectionProperty(
        type=AC_LayoutCollection,
        name="Collections"
    )

    is_expanded: BoolProperty(
        name="Expanded",
        description="UI list expansion state",
        default=False
    )

    collection_index: IntProperty(
        name="Active Collection Index",
        description="Currently selected collection in UIList",
        default=0
    )

    def get_collection_enabled(self, collection_name: str) -> bool:
        """Check if a collection is enabled in this layout"""
        for col in self.collections:
            if col.collection_name == collection_name:
                return col.enabled
        # Default to True if not explicitly disabled
        return True

    def set_collection_enabled(self, collection_name: str, enabled: bool):
        """Set whether a collection is enabled in this layout"""
        # Find existing entry
        for col in self.collections:
            if col.collection_name == collection_name:
                col.enabled = enabled
                return

        # Add new entry
        col = self.collections.add()
        col.collection_name = collection_name
        col.enabled = enabled

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "collections": [col.to_dict() for col in self.collections]
        }

    def from_dict(self, data: dict):
        self.name = data.get("name", "layout")
        self.collections.clear()
        for col_data in data.get("collections", []):
            col = self.collections.add()
            col.from_dict(col_data)


class AC_LayoutSettings(PropertyGroup):
    """Root layout management PropertyGroup"""

    layouts: CollectionProperty(
        type=AC_TrackLayout,
        name="Track Layouts"
    )

    active_layout_index: IntProperty(
        name="Active Layout",
        description="Currently selected layout for preview",
        default=0
    )

    collection_list_index: IntProperty(
        name="Collection List Index",
        description="Selected collection in UIList (unused, just for template_list)",
        default=0
    )

    preview_mode: BoolProperty(
        name="Preview Mode",
        description="When enabled, shows only active layout's collections",
        default=False,
        update=lambda self, context: self.toggle_preview_mode(context)
    )

    visibility_backup: StringProperty(
        name="Visibility Backup",
        description="JSON backup of collection visibility before preview",
        default="",
        options={'HIDDEN'}
    )

    def toggle_preview_mode(self, context):
        """Toggle collection visibility based on preview mode"""
        if self.preview_mode:
            # Enable preview mode - hide collections not in active layout
            self.apply_preview(context)
        else:
            # Disable preview mode - restore original visibility
            self.restore_visibility(context)

    def apply_preview(self, context):
        """Apply preview mode - show only active layout's collections"""
        if not self.layouts or self.active_layout_index >= len(self.layouts):
            return

        # Backup current visibility state
        visibility_backup = {}
        for col in bpy.data.collections:
            visibility_backup[col.name] = {
                'hide_viewport': col.hide_viewport,
                'hide_render': col.hide_render
            }
        self.visibility_backup = json.dumps(visibility_backup)

        # Get active layout
        active_layout = self.layouts[self.active_layout_index]

        # Show/hide collections based on layout state
        for col in bpy.data.collections:
            is_enabled = active_layout.get_collection_enabled(col.name)
            if is_enabled:
                col.hide_viewport = False
                col.hide_render = False
            else:
                col.hide_viewport = True
                col.hide_render = True

    def restore_visibility(self, context):
        """Restore original collection visibility"""
        if not self.visibility_backup:
            return

        try:
            visibility_backup = json.loads(self.visibility_backup)
            for col_name, visibility in visibility_backup.items():
                if col_name in bpy.data.collections:
                    col = bpy.data.collections[col_name]
                    col.hide_viewport = visibility['hide_viewport']
                    col.hide_render = visibility['hide_render']
        except (json.JSONDecodeError, KeyError):
            pass

        self.visibility_backup = ""

    def get_active_layout(self):
        """Get the currently active layout"""
        if self.layouts and 0 <= self.active_layout_index < len(self.layouts):
            return self.layouts[self.active_layout_index]
        return None

    def ensure_base_track_collection(self):
        """Ensure first collection is named 'base_track'"""
        if len(bpy.data.collections) == 0:
            # Create base_track collection if none exist
            col = bpy.data.collections.new("base_track")
            bpy.context.scene.collection.children.link(col)
        elif len(bpy.data.collections) > 0:
            # Rename first collection to base_track
            first_col = bpy.data.collections[0]
            if first_col.name != "base_track":
                first_col.name = "base_track"

    def ensure_default_layout(self):
        """Ensure there is always a default layout that cannot be deleted"""
        self.ensure_base_track_collection()

        if len(self.layouts) == 0:
            # Create default layout
            default_layout = self.layouts.add()
            default_layout.name = "default"
            self.active_layout_index = 0

    def to_dict(self) -> dict:
        return {
            "layouts": [layout.to_dict() for layout in self.layouts]
        }

    def from_dict(self, data: dict):
        self.layouts.clear()
        for layout_data in data.get("layouts", []):
            layout = self.layouts.add()
            layout.from_dict(layout_data)
        self.active_layout_index = 0

    def export_models_ini(self, working_dir: str) -> list[str]:
        """Export models_[layout].ini files for all layouts.

        Args:
            working_dir: Root directory for track files

        Returns:
            List of generated file paths
        """
        import bpy
        import os

        generated_files = []

        for layout in self.layouts:
            # Get enabled collections from scene
            enabled_collections = []
            for col in bpy.data.collections:
                if layout.get_collection_enabled(col.name):
                    enabled_collections.append(col.name)

            if not enabled_collections:
                continue

            # Generate INI content
            ini_lines = []
            for model_index, col_name in enumerate(enabled_collections):
                # Convert collection name to KN5 filename
                # Sanitize name: replace spaces/special chars with underscores
                kn5_name = col_name.replace(" ", "_").replace("-", "_")
                kn5_name = "".join(c if c.isalnum() or c == "_" else "_" for c in kn5_name)

                ini_lines.append(f"[MODEL_{model_index}]")
                ini_lines.append(f"FILE={kn5_name}.kn5")
                ini_lines.append("POSITION=0,0,0")
                ini_lines.append("ROTATION=0,0,0")
                ini_lines.append("")

            # Write models.ini for first layout, models_[layout].ini for others
            layout_index = list(self.layouts).index(layout)
            if layout_index == 0:
                ini_filename = "models.ini"
            else:
                ini_filename = f"models_{layout.name}.ini"
            ini_path = os.path.join(working_dir, ini_filename)

            try:
                with open(ini_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(ini_lines))
                generated_files.append(ini_path)
            except Exception:
                # Silently fail - caller should handle error reporting
                pass

        return generated_files
