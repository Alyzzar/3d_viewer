import pygame

class ViewControl:
    def __init__(self, width=800, height=600):
        self.view_mode = "perspective"  # 'perspective' or 'orthogonal'
        self.width = width
        self.height = height
        self.key_states = {}
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.persp_zoom = -5.0  # Perspective zoom
        self.ortho_zoom = 0.0   # Orthogonal zoom (scale factor)
        self.zoom = self.persp_zoom
        self.rot_x = 0.0  # Default rotation around x-axis
        self.rot_y = 0.0  # Default rotation around y-axis
        self.shift_held = False
        self.last_left_click = None  # (x, y) coordinates
        
    def reset_isometric_view(self):
        # Set rotation for top-left isometric view
        self.rot_x = 35.264  # ~35.264 degrees for isometric projection
        self.rot_y = 45.0    # 45 degrees for isometric projection
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.zoom = -5.0  # Reset zoom to default
        
    def toggle_view_mode(self):
        """Toggle between perspective and orthogonal view modes, normalizing zoom."""
        if self.view_mode == "perspective":
            self.persp_zoom = self.zoom
            self.view_mode = "orthogonal"
            self.zoom = self.ortho_zoom
        else:
            self.ortho_zoom = self.zoom
            self.view_mode = "perspective"
            self.zoom = self.persp_zoom

    def handle_mousemotion(self, event):
        # Middle mouse button: rotation
        # Shift + middle mouse button: panning
        # Scroll: zoom (handled in mousebuttondown)
        if event.buttons[1]:  # Middle mouse button held
            if self.shift_held:
                # Panning
                self.pan_x += event.rel[0] * 0.01
                self.pan_y -= event.rel[1] * 0.01
            else:
                # Rotation
                self.rot_x += event.rel[1] * 0.5
                self.rot_y += event.rel[0] * 0.5


    def handle_mousebuttondown(self, event):
        # Mouse wheel scroll for zoom
        if event.button == 4:  # Scroll up
            self.zoom += 0.5
            if self.view_mode == "perspective":
                self.persp_zoom = self.zoom
            else:
                self.ortho_zoom = self.zoom
        elif event.button == 5:  # Scroll down
            self.zoom -= 0.5
            if self.view_mode == "perspective":
                self.persp_zoom = self.zoom
            else:
                self.ortho_zoom = self.zoom
        elif event.button == 1:  # Left click
            self.last_left_click = event.pos

    def consume_left_click(self):
        click = self.last_left_click
        self.last_left_click = None
        return click

    def handle_mousebuttonup(self, event):
        pass

    def set_key_state(self, key, pressed):
        self.key_states[key] = pressed
        # Example: update shift_held for compatibility
        if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.shift_held = pressed

    def is_key_pressed(self, key):
        return self.key_states.get(key, False)

    def get_key_states(self):
        return self.key_states

    def handle_keydown(self, event):
        self.set_key_state(event.key, True)
        match event.key:
            case pygame.K_v:
                self.reset_isometric_view()
            case pygame.K_o:
                self.toggle_view_mode()

    def handle_keyup(self, event):
        self.set_key_state(event.key, False)
