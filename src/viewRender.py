# ---------------------------------------------
# Imports
# ---------------------------------------------
from abc import ABC, abstractmethod
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from models.model import Model, create_cube
from viewControl import ViewControl

# ---------------------------------------------
# Global variables
# ---------------------------------------------
debug = 2  # 0 = off, 1 = debug, 2 = full logging

# ---------------------------------------------
# Helper classes
# ---------------------------------------------
class RenderMode(ABC):
    def _compute_normalization_params(self):
        size = self.view_render.get_max_model_size()
        base_ortho = max(size, 1.0) * 1.5
        face_screen_size = self.view_render.get_closest_face_screen_size()
        target_size = 200.0
        scale = face_screen_size / target_size if face_screen_size > 0 else 1.0
        ortho_base_size = base_ortho / scale
        if debug >= 1:
            print(f"[DEBUG] NormalizationParams: size={size:.2f}, base_ortho={base_ortho:.2f}, face_screen_size={face_screen_size:.2f}, scale={scale:.4f}, ortho_base_size={ortho_base_size:.4f}")
        return size, base_ortho, face_screen_size, target_size, scale, ortho_base_size
    
    def __init__(self, view_render):
        self.view_render = view_render

    @abstractmethod
    def apply_projection(self):
        pass

    @abstractmethod
    def convert_zoom(self, zoom):
        pass

class PerspectiveMode(RenderMode):
    def normalize_view(self):
        size, base_ortho, face_screen_size, target_size, scale, ortho_base_size = self._compute_normalization_params()
        self.view_render.view_control.persp_zoom = -max(2.5 * size, 5.0)
        self.view_render.view_control.zoom = self.view_render.view_control.persp_zoom
        self.view_render.ortho_base_size = ortho_base_size

    def apply_projection(self):
        aspect = self.view_render.width / self.view_render.height
        gluPerspective(45, aspect, 0.1, 50.0)

    def convert_zoom(self, ortho_zoom=None):
        # Convert ortho zoom to perspective zoom
        k = 0.15
        base = getattr(self.view_render, 'ortho_base_size', 1.0)
        if ortho_zoom is None:
            ortho_zoom = getattr(self.view_render.view_control, 'ortho_zoom', 0.0)
        return -base / np.exp(ortho_zoom * k)

class OrthoMode(RenderMode):
    def normalize_view(self):
        size, base_ortho, face_screen_size, target_size, scale, ortho_base_size = self._compute_normalization_params()
        self.view_render.ortho_base_size = ortho_base_size
        k = 0.15
        persp_zoom = getattr(self.view_render.view_control, 'persp_zoom', -max(2.5 * size, 5.0))
        base = ortho_base_size
        if base > 0 and abs(persp_zoom) > 1e-6:
            self.view_render.view_control.ortho_zoom = (1.0 / k) * np.log(base / abs(persp_zoom))
        else:
            self.view_render.view_control.ortho_zoom = 0.0
        self.view_render.view_control.zoom = self.view_render.view_control.ortho_zoom
        if debug >= 1:
            print(f"[DEBUG] OrthoMode.normalize_view: persp_zoom={persp_zoom:.4f}, ortho_zoom={self.view_render.view_control.ortho_zoom:.4f}")

    def apply_projection(self):
        aspect = self.view_render.width / self.view_render.height
        base = getattr(self.view_render, 'ortho_base_size', 1.0)
        k = 0.15
        ortho_zoom = getattr(self.view_render.view_control, 'ortho_zoom', 0.0)
        scale = np.exp(ortho_zoom * k)
        ortho_size = base / scale
        glOrtho(-ortho_size * aspect, ortho_size * aspect, -ortho_size, ortho_size, -100, 100)

    def convert_zoom(self, persp_zoom=None):
        # Convert perspective zoom to ortho zoom
        k = 0.15
        base = getattr(self.view_render, 'ortho_base_size', 1.0)
        if persp_zoom is None:
            persp_zoom = getattr(self.view_render.view_control, 'persp_zoom', self.view_render.view_control.zoom)
        if base > 0 and abs(persp_zoom) > 1e-6:
            return (1.0 / k) * np.log(base / abs(persp_zoom))
        else:
            return 0.0
        
class ViewUtils:
    @staticmethod
    def get_closest_face_to_camera(models, view_matrix):
        closest_dist = float('inf')
        closest_face = None
        closest_verts = None
        for model in models:
            for face in getattr(model, 'faces', []):
                verts = [np.array(model.vertices[i]) for i in face]
                # Transform vertices by view matrix
                verts_cam = [view_matrix @ np.append(v, 1.0) for v in verts]
                # Use average z as distance to camera
                avg_z = np.mean([v[2] for v in verts_cam])
                if avg_z < closest_dist:
                    closest_dist = avg_z
                    closest_face = face
                    closest_verts = verts
        return closest_face, closest_verts

    @staticmethod
    def project_vertices_to_screen(vertices, modelview, projection, viewport):
        # Project 3D vertices to 2D screen coordinates
        screen_coords = []
        for v in vertices:
            win = gluProject(v[0], v[1], v[2], modelview, projection, viewport)
            screen_coords.append(win[:2])
        return np.array(screen_coords)
    
class ViewRender:
    # ---------------------------------------------
    # Main render loop: draws models and handles picking
    # ---------------------------------------------
    def render(self):
        vc = self.view_control
        # If view mode just changed, update normalization and convert zoom
        if getattr(self, 'last_view_mode', None) != vc.view_mode:
            self.get_render_mode().normalize_view()
            self.last_view_mode = vc.view_mode
        self.init_opengl()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(vc.pan_x, vc.pan_y, vc.zoom)
        glRotatef(vc.rot_x, 1, 0, 0)
        glRotatef(vc.rot_y, 0, 1, 0)

        # Check for new left click and perform picking
        click = vc.consume_left_click()
        if click:
            self.highlighted_face = self.pick_face(click[0], click[1])

        # Render faces first (if available)
        self.render_faces()
        # Render wireframes
        for model in self.models:
            model.render(self.screen)

        pygame.display.flip()
    def get_render_mode(self):
        mode = getattr(self.view_control, 'view_mode', 'perspective')
        if mode == 'orthogonal':
            return OrthoMode(self)
        else:
            return PerspectiveMode(self)

    # ---------------------------------------------
    # Get screen-space size of closest face to camera
    # ---------------------------------------------
    def get_closest_face_screen_size(self):
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        # Use identity for view_matrix for now (camera at origin)
        view_matrix = np.eye(4)
        _, verts = ViewUtils.get_closest_face_to_camera(self.models, view_matrix)
        if verts is None:
            return 1.0
        screen_coords = ViewUtils.project_vertices_to_screen(verts, modelview, projection, viewport)
        # Use max distance between any two screen coords as size
        dists = [np.linalg.norm(a-b) for i,a in enumerate(screen_coords) for b in screen_coords[i+1:]]
        return max(dists) if dists else 1.0
    
    # ---------------------------------------------
    # Compute the bounding box and max size of all models
    # ---------------------------------------------
    def get_max_model_size(self):
        if not self.models:
            return 1.0
        all_vertices = np.concatenate([np.array(m.vertices) for m in self.models if hasattr(m, 'vertices')])
        min_v = np.min(all_vertices, axis=0)
        max_v = np.max(all_vertices, axis=0)
        size = np.linalg.norm(max_v - min_v)
        return size if size > 0 else 1.0
    # ---------------------------------------------
    # Ray picking: Returns (model_idx, face_idx) if a face is picked, else None
    # ---------------------------------------------
    def pick_face(self, mouse_x, mouse_y):
        from OpenGL.GL import glGetIntegerv, glGetDoublev
        from OpenGL.GLU import gluUnProject
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        winX = float(mouse_x)
        winY = float(viewport[3] - mouse_y)
        near = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
        far = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)
        ray_dir = np.array(far) - np.array(near)
        ray_dir = ray_dir / np.linalg.norm(ray_dir)
        ray_origin = np.array(near)
        for m_idx, model in enumerate(self.models):
            for f_idx, face in enumerate(model.faces):
                verts = [np.array(model.vertices[i]) for i in face]
                v0, v1, v2 = verts[0], verts[1], verts[2]
                normal = np.cross(v1 - v0, v2 - v0)
                normal = normal / np.linalg.norm(normal)
                d = -np.dot(normal, v0)
                denom = np.dot(normal, ray_dir)
                if abs(denom) < 1e-6:
                    continue
                t = -(np.dot(normal, ray_origin) + d) / denom
                if t < 0:
                    continue
                intersect = ray_origin + t * ray_dir
                tri1 = [verts[0], verts[1], verts[2]]
                tri2 = [verts[0], verts[2], verts[3]]
                if self.point_in_triangle(intersect, tri1) or self.point_in_triangle(intersect, tri2):
                    return (m_idx, f_idx)
        return None

    # ---------------------------------------------
    # Helper: Check if point p is inside triangle tri
    # ---------------------------------------------
    def point_in_triangle(self, p, tri):
        a, b, c = tri
        v0 = c - a
        v1 = b - a
        v2 = p - a
        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot02 = np.dot(v0, v2)
        dot11 = np.dot(v1, v1)
        dot12 = np.dot(v1, v2)
        invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * invDenom
        v = (dot00 * dot12 - dot01 * dot02) * invDenom
        return (u >= 0) and (v >= 0) and (u + v <= 1)
    # ---------------------------------------------
    # Constructor: Initializes the viewer window and state
    # ---------------------------------------------
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.models = []
        self.view_control = ViewControl()
        self.init_pygame()
        self.init_opengl()
        # Set initial zoom (move camera back based on model size)
        self.reset_view()

    # ---------------------------------------------
    # Reset the view based on the max size of the current model(s)
    # ---------------------------------------------
    def reset_view(self):
        self.view_control.pan_x = 0
        self.view_control.pan_y = 0
        self.view_control.rot_x = 0
        self.view_control.rot_y = 0
        # Delegate all normalization and zoom logic to the current RenderMode
        self.get_render_mode().normalize_view()
        self.init_opengl()

    # ---------------------------------------------
    # Initialize pygame window
    # ---------------------------------------------
    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Environment Viewer')

    # ---------------------------------------------
    # Initialize OpenGL context and settings
    # ---------------------------------------------
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.get_render_mode().apply_projection()
        glMatrixMode(GL_MODELVIEW)

    # ---------------------------------------------
    # Add a model to the viewer
    # ---------------------------------------------
    def add_model(self, model):
        self.models.append(model)
        self.reset_view()  # Reset view when new model is added

    # ---------------------------------------------
    # Render all model faces with coloring and highlighting
    # ---------------------------------------------
    def render_faces(self):
        view_dir = np.array([0, 0, -1])
        def get_face_color(m_idx, f_idx, dot):
            if hasattr(self, 'highlighted_face') and self.highlighted_face == (m_idx, f_idx):
                return (1.0, 1.0, 0.2, 0.8)  # Yellow, more opaque
            elif dot > 0:
                return (0.2, 0.8, 0.2, 0.5)  # Green, semi-transparent
            else:
                return (0.8, 0.2, 0.2, 0.5)  # Red, semi-transparent
        for m_idx, model in enumerate(self.models):
            if hasattr(model, 'faces') and model.faces:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glBegin(GL_QUADS)
                for f_idx, face in enumerate(model.faces):
                    v0 = np.array(model.vertices[face[0]])
                    v1 = np.array(model.vertices[face[1]])
                    v2 = np.array(model.vertices[face[2]])
                    normal = np.cross(v1 - v0, v2 - v0)
                    normal = normal / np.linalg.norm(normal)
                    dot = np.dot(normal, view_dir)
                    color = get_face_color(m_idx, f_idx, dot)
                    glColor4f(*color)
                    for idx in face:
                        glVertex3fv(model.vertices[idx])
                glEnd()
                glDisable(GL_BLEND)

    # ---------------------------------------------
    # Main event loop: handles input and rendering
    # ---------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        vc = self.view_control
        while True:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        return
                    case pygame.KEYDOWN:
                        vc.handle_keydown(event)
                    case pygame.KEYUP:
                        vc.handle_keyup(event)
                    case pygame.MOUSEBUTTONDOWN:
                        vc.handle_mousebuttondown(event)
                    case pygame.MOUSEBUTTONUP:
                        vc.handle_mousebuttonup(event)
                    case pygame.MOUSEMOTION:
                        vc.handle_mousemotion(event)

            self.render()
            clock.tick(60)

if __name__ == "__main__":
    viewer = ViewRender()
    model = create_cube()
    viewer.add_model(model)
    viewer.run()