import pygame
from OpenGL.GL import *

class WireframeModel:
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def add_edge(self, edge):
        self.edges.append(edge)

    def render(self, screen=None):
        glColor3f(1.0, 1.0, 1.0)  # White color
        glBegin(GL_LINES)
        for edge in self.edges:
            start, end = edge
            glVertex3fv(self.vertices[start])
            glVertex3fv(self.vertices[end])
        glEnd()

def create_cube():
    vertices = [
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1)
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    return WireframeModel(vertices, edges)