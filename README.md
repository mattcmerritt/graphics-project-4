# graphics-project-4

This code is the full scene for Project 4: Ray Tracer, done by Matthew Merritt, Michael Merritt, and Harsh Gandhi. 

## Running the Scene

Ensure that you have the following python packages installed:

```
decorator==5.1.1
imageio==2.36.1
imageio-ffmpeg==0.5.1
moviepy==2.1.1
numpy==2.2.0
pillow==10.4.0
proglog==0.1.10
pygame==2.6.0
PyOpenGL==3.1.7
python-dotenv==1.0.1
setuptools==75.6.0
tqdm==4.67.1
```

Once the packages are installed, run the following:

```bash
python main_simple.py
```

An additional window should open with the interactive 3D scene.

Once frames are generated, you can create a video using the following command:

```bash
python stitcher.py -output video_name.mp4 frame*.png
```

## Files

Notable code changes from the base code provided in class include:

- `main_simple.py` - Contains the interactive 3D scene with lights, objects, and player controls. This is the file that should be run.
- `Light.py` - Support class for the lighting, includes some adjustments to support shadows for directional and point lights. Spot lights are NOT supported.
- `Scene.py` - Class for representing a complete scene with objects, supporting OpenGL and raytracing. Minor adjustments were made to support texturing surfaces.
- `GeomObj.py` - Base class for shapes that support rendering in OpenGL and in the raytraced scene. Inlcudes support for loading textures and bump maps.
- `SphereObj.py` - Implementation of `GeomObj` for spherical objects. Minor adjustments were made to support texturing surfaces. Currently, spheres cannot be textured and do not use the bump maps.
- `BoxObj.py` - Implementation of `GeomObj` for rectangular prism objects. Now includes the intersection test and textured rendering. Texturing supports a single texture which will be repeated on all six faces. Also supports loading a bump map to adjust the normals used in lighting calculations for all six faces.
- `CylinderObj.py` - Implementation of `GeomObj` for conic and cylindrical objects. Includes the intersection test. Currently, cylinders cannot be textured and do not use the bump maps.

All textures are available in the `resources` directory.

## Features

The features are the following:

- Scene construction - Scene is included with walls, cieling, floor, and an assortment of shapes.
- Box ray intersection - Rays will intersect boxes on all six faces, without any surface errors. The hit location, norm, and texture color are all returned.
- Cylinder ray intersection - Rays will intersect cylinders on both the inside and outside faces. The hit location and norm are returned.
- Texture mapping - Boxes support texture mapping, and are tiled to allow wrapping around corners. These textures are applied multiplicatively when raytracing (effectively similar to GL_MODULATE texturing mode).
- Bump mapping - Boxes support bump mapping / normal mapping, allowing additional adjustments to be made the the lighting calculations to give an illusion of detail.

### Controls

Manual Camera Controls:
- W/S               - Move forward/backward
- A/D               - Strafe left/right
- Q/E               - Move camera up/down
- Left/Right        - Turn camera left/right
- Up/Down           - Tilt camera up/down

Interpolated Camera Controls:
- Equals (=)        - Increase camera speed
- Minus (-)         - Decrease camera speed
- Slash (/)         - Stop camera motion

Raytracing Contorls:
- Space             - Pause/resume animation
- Backtick (`)      - Render a single image
- Backslash (\\)    - Begin/stop recording frames
- Period (.)        - Stop moving light

System Controls:
  H - Show help message
  ESC - Exit program