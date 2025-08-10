import pygame
import numpy as np
from OpenGL.GL import *

class Model:
    def __init__(self, vertices, edges, faces=None):
        self.vertices = vertices
        self.edges = edges
        self.faces = faces if faces is not None else []

    def add_face(self, face):
        self.faces.append(face)

    def render_faces(self, screen=None, highlight_faces=None):
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.2, 0.6, 1.0, 0.3)  # Light blue, low opacity
        glBegin(GL_QUADS)
        for i, face in enumerate(self.faces):
            if highlight_faces and i in highlight_faces:
                glColor4f(1.0, 0.8, 0.2, 0.6)  # Highlight color, higher opacity
            else:
                glColor4f(0.2, 0.6, 1.0, 0.3)
            for idx in face:
                glVertex3fv(self.vertices[idx])
        glEnd()
        glDisable(GL_BLEND)

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def add_edge(self, edge):
        self.edges.append(edge)

    def render(self, screen=None, highlight_faces=None):
        self.render_faces(screen, highlight_faces)
        glColor3f(1.0, 1.0, 1.0)  # White color
        glBegin(GL_LINES)
        for edge in self.edges:
            start, end = edge
            glVertex3fv(self.vertices[start])
            glVertex3fv(self.vertices[end])
        glEnd()

# ---------------------------------------------
# Polar coordinate class for creating models
# ---------------------------------------------
class Polar:
    def __init__(self, radius, angle):
        self.radius = radius
        self.angle = angle

    def to_cartesian(self):
        return (
            self.radius * np.cos(self.angle),
            self.radius * np.sin(self.angle),
            0.0
        )

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
    faces = [
        [0, 1, 2, 3],  # Bottom
        [4, 5, 6, 7],  # Top
        [0, 1, 5, 4],  # Front
        [2, 3, 7, 6],  # Back
        [1, 2, 6, 5],  # Right
        [0, 3, 7, 4],  # Left
    ]
    return Model(vertices, edges, faces)

def create_donut():
    vertices = []
    edges = []
    faces = []
    # Use polar coordinates to quickly create a low poly donut with 12 sides
    num_sides = 12
    for i in range(num_sides):
        angle = 2 * np.pi * i / num_sides
        for j in range(num_sides):
            sub_angle = 2 * np.pi * j / num_sides
            radius = 1.0 + 0.5 * np.cos(sub_angle)
            z = 0.5 * np.sin(sub_angle)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append((x, y, z))
            if i < num_sides - 1 and j < num_sides - 1:
                # Create faces for the donut
                idx1 = i * num_sides + j
                idx2 = idx1 + 1
                idx3 = (i + 1) * num_sides + j + 1
                idx4 = (i + 1) * num_sides + j
                faces.append([idx1, idx2, idx3, idx4])
                edges.append((idx1, idx2))
                edges.append((idx2, idx3))
                edges.append((idx3, idx4))
                edges.append((idx4, idx1))
    
