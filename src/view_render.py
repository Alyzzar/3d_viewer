import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from models.wireframe import WireframeModel, create_cube
from view_control import ViewControl

class Viewer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.models = []
        self.init_pygame()
        self.init_opengl()
        self.view_control = ViewControl()

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Environment Viewer')

    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def add_model(self, model):
        self.models.append(model)

    def render(self):
        vc = self.view_control
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(vc.pan_x, vc.pan_y, vc.zoom)
        glRotatef(vc.rot_x, 1, 0, 0)
        glRotatef(vc.rot_y, 0, 1, 0)

        for model in self.models:
            model.render(self.screen)

        pygame.display.flip()

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
    viewer = Viewer()
    wireframe_model = create_cube()
    viewer.add_model(wireframe_model)
    viewer.run()