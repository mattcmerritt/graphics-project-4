"""
A basic (but far from simple) ray tracer.

Author: Christian Duncan
Course: CSC345/645: Computer Graphics
Term: Fall 2024

This code provides the main interface to a ray tracing project. It allows navigation of a simple
scene and then the ability to render that scene using ray tracing. The implementation is SLOW.
But making it efficient is an entirely more complex task.
"""

import sys
import math
import pygame
import copy
from OpenGL.GLU import *
from OpenGL.GL import *
from Navigator import Navigator
from Camera import Camera
from Point3 import Point3
from Vector3 import Vector3
from Window import Window
from Scene import Scene
from SphereObj import SphereObj
from BoxObj import BoxObj
from CylinderObj import CylinderObj
from Material import Material
from Light import Light
from Color import Color

# Constants
FPS = 60
FRAME_WIDTH = 500
FRAME_HEIGHT = 500
FRAME_TITLE = "Go Ray Tracer!"
# DELAY = int(1000 / FPS)

# Initialize global variables
init_eye = Point3(0, 0, 10)
init_look = Point3(0, 0, 0)
init_up = Vector3(0, 1, 0)
# TODO: remove overhead view
# init_eye = Point3(-7.291, 8.583, 7.718)
# init_look = Point3(-7.291 - (-0.57356), 8.583 - (0.51504), 7.718 - (0.63700))
init_view_angle = 45.0
init_near = 0.1
init_far = 50.0

nav = Navigator(Camera(init_eye, init_look, init_up))
win = Window(FRAME_WIDTH, FRAME_HEIGHT, FRAME_TITLE)
scn = Scene()
light_angle = 0
light_speed = 1
# TODO: remove faster speed
# light_speed = 10
light_distance = 5
animate = True  # Animation

# Enums for rendering modes
RENDER_SOLID = 0
RENDER_RAY_SINGLE = 1
RENDER_RAY_RECORD = 2
render_mode = RENDER_SOLID
raytrace_count = 0  # How many ray traced images have been generated so far

block_size = 4

# Functions
def set_looping_light_positions(lightA):
    global light_angle, light_distance
    pos_x = light_distance * math.cos(math.radians(light_angle))
    pos_y = light_distance * math.sin(math.radians(light_angle))
    pos_z = 0

    lightA.set_position(pos_x, pos_y, pos_z)
    lightA.obj.reset()
    lightA.obj.translate(pos_x, pos_y, pos_z)
    lightA.obj.scale(0.2, 0.2, 0.2)

def init_scene():
    global scn, nav, lightA

    # Setup camera
    cam = nav.get_camera()
    cam.look_at(init_eye, init_look, init_up)
    cam.set_lens_shape(init_view_angle, FRAME_WIDTH / FRAME_HEIGHT, init_near, init_far)

    # boxes
    mat = Material()
    mat.set_gold()
    mat.set_reflectivity(0.4)
    textured_box_1 = BoxObj()
    textured_box_1.set_material(mat)
    textured_box_1.translate(0,1,-10)
    textured_box_1.scale(0.5, 0.5, 0.5)
    textured_box_1.rotate(45, Vector3(0, 1, 0))
    textured_box_1.rotate(45, Vector3(1, 0, 0))
    textured_box_1.name = "Box 1"
    scn.add_object(textured_box_1)

    mat = Material()
    mat.set_chrome()
    mat.set_reflectivity(0.7)
    textured_box_2 = BoxObj()
    textured_box_2.set_texture('resources/example_texture.png', 128)
    textured_box_2.set_material(mat)
    textured_box_2.translate(10,1,11)
    textured_box_2.scale(1, 2, 1)
    textured_box_2.name = "Box 2"
    scn.add_object(textured_box_2)

    mat = Material()
    mat.set_pewter()
    mat.set_reflectivity(0.3)
    textured_box_3 = BoxObj()
    textured_box_3.set_texture('resources/striped.png', 128)
    textured_box_3.set_normal_map('resources/beveled_edges.png')
    textured_box_3.set_material(mat)
    textured_box_3.translate(-7,0.5,-7)
    textured_box_3.scale(0.75, 0.75, 0.75)
    textured_box_3.rotate(45, Vector3(0, 1, 0))
    textured_box_3.rotate(45, Vector3(1, 0, 0))
    textured_box_3.name = "Box 3"
    scn.add_object(textured_box_3)

    mat = Material()
    mat.set_silver()
    mat.set_reflectivity(0.1)
    mat.set_shininess(10)
    textured_box_4 = BoxObj()
    textured_box_4.set_texture('resources/grid.png', 128)
    textured_box_4.set_normal_map('resources/grid.png')
    textured_box_4.set_material(mat)
    textured_box_4.translate(-6,0,10)
    textured_box_4.rotate(45, Vector3(0, 1, 0))
    textured_box_4.name = "Box 4"
    scn.add_object(textured_box_4)

    # tapered cylinders
    mat = Material()
    mat.set_copper()
    mat.set_reflectivity(0.7)
    tube = CylinderObj(1, 2, 3)
    tube.set_material(mat)
    tube.translate(8,1,2)
    tube.scale(1, 1, 1)
    tube.name = "Tube 1"
    scn.add_object(tube)

    mat = Material()
    mat.set_gold()
    mat.set_reflectivity(0.7)
    tube2 = CylinderObj(0, 1, 3)
    tube2.set_material(mat)
    tube2.translate(-9,1,0)
    tube2.rotate(90, Vector3(1, 0, 0))
    tube2.scale(1, 1, 1)
    tube2.name = "Tube 2"
    scn.add_object(tube2)

    mat = Material()
    mat.set_pewter()
    mat.set_reflectivity(0.1)
    tube3 = CylinderObj(2, 1, 3)
    tube3.set_material(mat)
    tube3.translate(-10,1,-4)
    tube3.scale(1, 1, 1)
    tube3.name = "Tube 3"
    scn.add_object(tube3)

    mat = Material()
    mat.set_silver()
    mat.set_reflectivity(0.4)
    tube4 = CylinderObj(1, 1, 5)
    tube4.set_material(mat)
    tube4.translate(4,3,-3)
    tube4.rotate(90, Vector3(1, 0, 0))
    tube4.scale(1, 1, 1)
    tube4.name = "Tube 4"
    scn.add_object(tube4)

    # balls
    mat = Material()
    mat.set_copper()
    mat.set_reflectivity(0.4)
    ball1 = SphereObj()
    ball1.set_material(mat)
    ball1.translate(-2,0,-10)
    ball1.scale(1, 1, 1)
    ball1.name = "Ball 1"
    scn.add_object(ball1)

    mat = Material()
    mat.set_silver()
    mat.set_reflectivity(0.4)
    ball2 = SphereObj()
    ball2.set_material(mat)
    ball2.translate(2,0,-10)
    ball2.scale(1, 1, 1)
    ball2.name = "Ball 2"
    scn.add_object(ball2)

    mat = Material()
    mat.set_gold()
    mat.set_reflectivity(0.1)
    ball3 = SphereObj()
    ball3.set_material(mat)
    ball3.translate(8,1,0)
    ball3.scale(1, 2, 1)
    ball3.name = "Ball 3"
    scn.add_object(ball3)

    mat = Material()
    mat.set_chrome()
    mat.set_reflectivity(0.7)
    ball4 = SphereObj()
    ball4.set_material(mat)
    ball4.translate(-10,0,3)
    ball4.scale(2, 1, 2)
    ball4.name = "Ball 4"
    scn.add_object(ball4)

    # walls
    mat = Material()
    mat.set_silver()
    mat.set_reflectivity(0.3)
    floor = BoxObj()
    floor.name = "Floor"
    floor.set_material(mat)
    floor.translate(0, -2, 0)
    floor.scale(15, 0.1, 15)
    scn.add_object(floor)

    mat = Material() # uses the flat default material
    mat.set_reflectivity(0.1)
    forward_wall = BoxObj()
    forward_wall.set_texture('resources/lattice.png', 128)
    forward_wall.name = "Forward Wall"
    forward_wall.set_material(mat)
    forward_wall.translate(0, 3, -15)
    forward_wall.scale(15, 5, 1)
    scn.add_object(forward_wall)

    backward_wall = BoxObj()
    backward_wall.set_texture('resources/lattice.png', 128)
    backward_wall.name = "Backward Wall"
    backward_wall.set_material(mat)
    backward_wall.translate(0, 3, 15)
    backward_wall.scale(15, 5, 1)
    scn.add_object(backward_wall)

    left_wall = BoxObj()
    left_wall.set_texture('resources/lattice.png', 128)
    left_wall.name = "Left Wall"
    left_wall.set_material(mat)
    left_wall.translate(-15, 3, 0)
    left_wall.scale(1, 5, 14)
    scn.add_object(left_wall)

    right_wall = BoxObj()
    right_wall.set_texture('resources/lattice.png', 128)
    right_wall.name = "Right Wall"
    right_wall.set_material(mat)
    right_wall.translate(15, 3, 0)
    right_wall.scale(1, 5, 14)
    scn.add_object(right_wall)

    # Light setup
    lightA = Light()
    scn.add_light(lightA)
    mat = Material()
    mat.set_emissive_only(lightA.get_diffuse())
    mat.set_translucent(True)

    # Create a visible component of the light
    # It will be associated both with the light and with the Scene
    lightA.obj = SphereObj()
    lightA.obj.name = "Light Source A"
    lightA.obj.set_material(mat)
    scn.add_object(lightA.obj)

    set_looping_light_positions(lightA)

    # Stationary lights
    lightB = Light()
    scn.add_light(lightB)
    mat = Material()
    mat.set_emissive_only(lightB.get_diffuse())
    mat.set_translucent(True)
    lightB.obj = SphereObj()
    lightB.obj.name = "Light Source B"
    lightB.obj.set_material(mat)
    scn.add_object(lightB.obj)
    lightB.set_position(0, 5, -8)
    lightB.obj.reset()
    lightB.obj.translate(0, 5, -8)
    lightB.obj.scale(0.2, 0.2, 0.2)

    # Stationary lights
    lightC = Light()
    scn.add_light(lightC)
    mat = Material()
    mat.set_emissive_only(lightC.get_diffuse())
    mat.set_translucent(True)
    lightC.obj = SphereObj()
    lightC.obj.name = "Light Source C"
    lightC.obj.set_material(mat)
    scn.add_object(lightC.obj)
    lightC.set_position(-8, 5, 8)
    lightC.obj.reset()
    lightC.obj.translate(-8, 5, 8)
    lightC.obj.scale(0.2, 0.2, 0.2)

    # Stationary lights
    lightD = Light()
    scn.add_light(lightD)
    mat = Material()
    mat.set_emissive_only(lightD.get_diffuse())
    mat.set_translucent(True)
    lightD.obj = SphereObj()
    lightD.obj.name = "Light Source D"
    lightD.obj.set_material(mat)
    scn.add_object(lightD.obj)
    lightD.set_position(8, 5, 8)
    lightD.obj.reset()
    lightD.obj.translate(8, 5, 8)
    lightD.obj.scale(0.2, 0.2, 0.2)

# Return a copy of all the things in scene that could have changed!
def get_copy_state():
    return (copy.deepcopy(nav.camera), light_angle)

# Reset the state back to the given state
def restore_state(state):
    global nav, light_angle, lightA
    nav.camera = copy.deepcopy(state[0])
    light_angle = state[1]
    set_looping_light_positions(lightA)

def display():
    global render_mode, raytrace_count, animate, record
    if render_mode == RENDER_SOLID:
        scn.render_solid(nav.get_camera(), win)
        pygame.display.flip()
    elif render_mode == RENDER_RAY_SINGLE:
        scn.render_solid(nav.get_camera(), win)   # Render solid first so user can see it
        pygame.display.flip()
        scn.render_ray_traced(nav.get_camera(), win, block_size)
        win.save_pixmap('image{0}.png'.format(raytrace_count))
        raytrace_count+=1
        animate = False
        render_mode = RENDER_SOLID # So doesn't try to render it again!
        pygame.event.clear() # Takes so long to render, need to clear events that happened while rendering!
    elif render_mode == RENDER_RAY_RECORD:
        scn.render_solid(nav.get_camera(), win)   # Render solid first so user can see it
        pygame.display.flip()
        if len(record) < 60: # Capped so we don't go crazy ray tracing here!
            # Save a copy of the things that could change from scene to scene
            record.append(get_copy_state())

# Ray trace a sequence of frames - each step recorded to recreate
def raytrace_records(record):
    # Save the current state
    save_state = get_copy_state()

    record_count = 1
    for s in record:
        print("Recording frame {0} of {1}".format(record_count, len(record)))
        # Restore state back to this saved record
        restore_state(s)
        scn.render_solid(nav.get_camera(), win)   # Render solid first so user can see it
        pygame.display.flip()
        scn.render_ray_traced(nav.get_camera(), win, block_size)
        win.save_pixmap('frame{0:04}.png'.format(record_count))
        record_count+=1

    pygame.event.clear() # Takes so long to render, need to clear events that happened while rendering!

    # Restore it back
    restore_state(save_state)

def handle_events():
    global render_mode, block_size, light_speed, animate, record
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_1:
                block_size = 1
            elif event.key == pygame.K_2:
                block_size = 2
            elif event.key == pygame.K_3:
                block_size = 4
            elif event.key == pygame.K_BACKQUOTE:
                render_mode = RENDER_RAY_SINGLE
            elif event.key == pygame.K_BACKSLASH:
                if render_mode != RENDER_RAY_RECORD:
                    # Start the recording!
                    record = []
                    render_mode = RENDER_RAY_RECORD
                else:
                    # End it and begin ray tracing each image
                    raytrace_records(record)
                    render_mode = RENDER_SOLID
                    animate = False
                    render_mode = RENDER_SOLID # So doesn't try to render it again!
            elif event.key == pygame.K_SPACE:
                animate = not animate
            elif event.key == pygame.K_PERIOD:
                light_speed = 0
            else:
                nav.keyboard(event.key)
    return True

def main():
    global light_angle, light_distance, lightA, render_mode, animate
    win.initialize()
    init_scene()

    clock = pygame.time.Clock()
    running = True

    # Set up lighting and depth-test
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)    # Inefficient...
    glEnable(GL_DEPTH_TEST)   # For z-buffering!

    while running:
        running = handle_events()

        if animate:
            # Advance the navigator
            nav.advance()
   
            # Do any other animations needed (like moving objects around)
            # Move the main light around
            light_angle += light_speed
            if light_angle >= 360: light_angle -= 360
            elif light_angle < 0: light_angle += 360

            set_looping_light_positions(lightA)

        display()
        
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
