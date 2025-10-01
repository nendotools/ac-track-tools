import bpy
from bpy.props import StringProperty
from bpy.types import Operator


class AC_AddLayout(Operator):
    """Add a new track layout"""
    bl_idname = "ac.add_layout"
    bl_label = "Add Layout"
    bl_options = {'REGISTER', 'UNDO'}

    layout_name: StringProperty(
        name="Layout Name",
        description="Name for the new layout (max 15 characters)",
        default="layout",
        maxlen=15
    )

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        # Ensure base_track collection and default layout exist
        layout_settings.ensure_base_track_collection()

        # Validate name is not empty
        if not self.layout_name.strip():
            self.report({'ERROR'}, "Layout name cannot be empty")
            return {'CANCELLED'}

        # Check for duplicate names
        for layout in layout_settings.layouts:
            if layout.name == self.layout_name:
                self.report({'ERROR'}, f"Layout '{self.layout_name}' already exists")
                return {'CANCELLED'}

        # Create new layout (collections will be shown dynamically from scene)
        new_layout = layout_settings.layouts.add()
        new_layout.name = self.layout_name

        # Set as active layout
        layout_settings.active_layout_index = len(layout_settings.layouts) - 1

        self.report({'INFO'}, f"Added layout '{self.layout_name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        # If no layouts exist, create default without dialog
        if len(layout_settings.layouts) == 0:
            self.layout_name = "default"
            return self.execute(context)

        # Otherwise show name dialog for additional layouts
        # Reset to default value for the dialog
        self.layout_name = "layout"
        return context.window_manager.invoke_props_dialog(self)


class AC_RemoveLayout(Operator):
    """Remove the active track layout"""
    bl_idname = "ac.remove_layout"
    bl_label = "Remove Layout"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.AC_Settings
        # Can only remove if there's more than 1 layout (cannot delete default)
        return len(settings.layout_settings.layouts) > 1

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        if len(layout_settings.layouts) <= 1:
            self.report({'WARNING'}, "Cannot delete default layout")
            return {'CANCELLED'}

        # Get current active index
        active_idx = layout_settings.active_layout_index

        # Cannot delete first layout (default)
        if active_idx == 0:
            self.report({'WARNING'}, "Cannot delete default layout")
            return {'CANCELLED'}

        layout_name = layout_settings.layouts[active_idx].name

        # Remove the layout
        layout_settings.layouts.remove(active_idx)

        # Adjust active index if necessary
        if active_idx >= len(layout_settings.layouts):
            layout_settings.active_layout_index = max(0, len(layout_settings.layouts) - 1)

        self.report({'INFO'}, f"Removed layout '{layout_name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        if layout_settings.layouts:
            layout_name = layout_settings.layouts[layout_settings.active_layout_index].name
            return context.window_manager.invoke_confirm(
                self, event, message=f"Remove layout '{layout_name}'?"
            )
        return {'CANCELLED'}


class AC_RemoveLayoutByIndex(Operator):
    """Remove a specific track layout by index"""
    bl_idname = "ac.remove_layout_by_index"
    bl_label = "Remove Layout"
    bl_options = {'REGISTER', 'UNDO'}

    layout_index: StringProperty(
        name="Layout Index",
        description="Index of the layout to remove"
    )

    @classmethod
    def poll(cls, context):
        settings = context.scene.AC_Settings
        return len(settings.layout_settings.layouts) > 1

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        try:
            index = int(self.layout_index)
        except ValueError:
            return {'CANCELLED'}

        # Cannot delete first layout (default) or if only one layout
        if index == 0 or len(layout_settings.layouts) <= 1:
            self.report({'WARNING'}, "Cannot delete default layout")
            return {'CANCELLED'}

        if index < 0 or index >= len(layout_settings.layouts):
            return {'CANCELLED'}

        layout_name = layout_settings.layouts[index].name

        # Remove the layout
        layout_settings.layouts.remove(index)

        # Adjust active index if necessary
        if layout_settings.active_layout_index >= len(layout_settings.layouts):
            layout_settings.active_layout_index = max(0, len(layout_settings.layouts) - 1)
        elif layout_settings.active_layout_index >= index:
            # If we removed a layout before or at the active index, decrement
            layout_settings.active_layout_index = max(0, layout_settings.active_layout_index - 1)

        self.report({'INFO'}, f"Removed layout '{layout_name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        try:
            index = int(self.layout_index)
            if 0 <= index < len(layout_settings.layouts):
                layout_name = layout_settings.layouts[index].name
                return context.window_manager.invoke_confirm(
                    self, event, message=f"Remove layout '{layout_name}'?"
                )
        except (ValueError, IndexError):
            pass

        return {'CANCELLED'}


class AC_ToggleLayoutCollection(Operator):
    """Toggle collection visibility for the active layout"""
    bl_idname = "ac.toggle_layout_collection"
    bl_label = "Toggle Layout Collection"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: StringProperty(
        name="Collection Name",
        description="Name of the collection to toggle"
    )

    @classmethod
    def poll(cls, context):
        settings = context.scene.AC_Settings
        return len(settings.layout_settings.layouts) > 0

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        if not layout_settings.layouts:
            return {'CANCELLED'}

        active_layout = layout_settings.layouts[layout_settings.active_layout_index]

        # Prevent disabling the first/primary collection (first in scene)
        if len(bpy.data.collections) > 0 and bpy.data.collections[0].name == self.collection_name:
            current_enabled = active_layout.get_collection_enabled(self.collection_name)
            if current_enabled:
                self.report({'WARNING'}, "Cannot disable primary collection")
                return {'CANCELLED'}

        # Toggle the collection state
        current_enabled = active_layout.get_collection_enabled(self.collection_name)
        new_enabled = not current_enabled
        active_layout.set_collection_enabled(self.collection_name, new_enabled)

        # If in preview mode, update visibility immediately
        if layout_settings.preview_mode:
            if self.collection_name in bpy.data.collections:
                col = bpy.data.collections[self.collection_name]
                col.hide_viewport = not new_enabled  # Hide if NOT enabled
                col.hide_render = not new_enabled

        return {'FINISHED'}


class AC_SetActiveLayout(Operator):
    """Set the active layout for preview"""
    bl_idname = "ac.set_active_layout"
    bl_label = "Set Active Layout"
    bl_options = {'REGISTER', 'UNDO'}

    layout_index: StringProperty(
        name="Layout Index",
        description="Index of the layout to set as active"
    )

    @classmethod
    def poll(cls, context):
        settings = context.scene.AC_Settings
        return len(settings.layout_settings.layouts) > 0

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        try:
            index = int(self.layout_index)
        except ValueError:
            return {'CANCELLED'}

        if 0 <= index < len(layout_settings.layouts):
            layout_settings.active_layout_index = index

            # If in preview mode, update visibility
            if layout_settings.preview_mode:
                layout_settings.apply_preview(context)

            return {'FINISHED'}

        return {'CANCELLED'}


class AC_RefreshLayoutCollections(Operator):
    """Refresh all layouts to sync with current scene collections"""
    bl_idname = "ac.refresh_layout_collections"
    bl_label = "Refresh Layout Collections"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.AC_Settings
        return len(settings.layout_settings.layouts) > 0

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        # Get all current collection names
        current_collections = {col.name for col in bpy.data.collections}

        for layout in layout_settings.layouts:
            # Get existing collection names in this layout
            existing_in_layout = {lc.collection_name for lc in layout.collections}

            # Add new collections
            new_collections = current_collections - existing_in_layout
            for col_name in new_collections:
                layout_col = layout.collections.add()
                layout_col.collection_name = col_name
                layout_col.enabled = True

            # Remove deleted collections (iterate backwards to avoid index issues)
            for i in range(len(layout.collections) - 1, -1, -1):
                if layout.collections[i].collection_name not in current_collections:
                    layout.collections.remove(i)

        self.report({'INFO'}, "Refreshed all layouts with current collections")
        return {'FINISHED'}


class AC_ToggleLayoutExpand(Operator):
    """Toggle layout expansion in UI"""
    bl_idname = "ac.toggle_layout_expand"
    bl_label = "Toggle Layout Expand"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.AC_Settings
        return len(settings.layout_settings.layouts) > 0

    def execute(self, context):
        settings = context.scene.AC_Settings
        layout_settings = settings.layout_settings

        if layout_settings.layouts:
            active_layout = layout_settings.layouts[layout_settings.active_layout_index]
            active_layout.is_expanded = not active_layout.is_expanded

        return {'FINISHED'}
