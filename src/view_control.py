import pygame

class Viewer:
    def __init__(self, width=800, height=600):
        # ...existing code...
        self.key_states = {}
        # ...existing code...

    def set_key_state(self, key, pressed):
        self.key_states[key] = pressed
        # Example: update shift_held for compatibility
        if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.shift_held = pressed

    def get_key_states(self):
        return self.key_states

    def handle_keydown(self, event):
        self.set_key_state(event.key, True)
        match event.key:
            case pygame.K_v:
                self.reset_isometric_view()

    def handle_keyup(self, event):
        self.set_key_state(event.key, False)
