
from Matrix import Matrix
from Material import Material
from Ray import Ray
from Hit import Hit
from Color import Color
from Vector3 import Vector3
from OpenGL.GL import *
from PIL import Image

class GeomObj:
    def __init__(self):
        self.material = Material()
        self.matrix = Matrix()
        self.matrix_inverse = Matrix()
        self.matrix.load_identity()
        self.matrix_inverse.load_identity()
        self.name = "Unknown"   # Use a name to help identify the object for debugging

    def prepare_solid(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glMultMatrixf(self.matrix.m)
   
        # Prepare Material property
        self.material.set_material_OpenGL()

    def done_solid(self):
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def set_material(self, material):
        self.material = material

    def translate(self, dx, dy, dz):
        self.matrix.post_translate(dx, dy, dz)
        self.matrix_inverse.pre_translate(-dx, -dy, -dz)

    def scale(self, sx, sy, sz):
        self.matrix.post_scale(sx, sy, sz)
        self.matrix_inverse.pre_scale(1.0 / sx, 1.0 / sy, 1.0 / sz)

    def rotate(self, angle, axis):
        self.matrix.post_rotate(angle, axis)
        self.matrix_inverse.pre_rotate(-angle, axis)

    def intersect(self, ray, best_hit):
        transformed_ray = Ray(
            self.matrix_inverse.affine_mult_point(ray.source),
            self.matrix_inverse.affine_mult_vector(ray.dir)
        )
        if self.local_intersect(transformed_ray, best_hit):
            # Need to recompute the hit point in WORLD SPACE (using original ray)
            best_hit.point = ray.eval(best_hit.t)

            # Transform the normal in best_hit from OBJECT space to WORLD space
            # using the inverse transpose
            best_hit.norm = self.matrix_inverse.affine_transpose_mult_vector(best_hit.norm)
            best_hit.norm.normalize()
            return True
        return False

    """
      * Should be defined for each subclass of GeomObj.
      *    ray: Defined in the Object's space
      *    best_hit: Current best hit time
      *    returns: true if a closer hit was found
      *    IN ADDITION: If a closer hit was found then:
      *       1) best_hit.t should have the new hit "time"
      *       2) best_hit.point should have the point location (IN OBJECT SPACE) of the intersection
      *       3) best_hit.norm should contain normal at intersection (IN OBJECT SPACE)
      *       4) best_hit.obj should reference the object hit itself (self)
    """
    def local_intersect(self, ray, best_hit):
        raise NotImplementedError("Subclasses must implement local_intersect.")

    # TEXTURING
    """
    Attaching a texture to the shape.
    Textures will always fill the entire shape, and are not tiled.
    Requires all loaded textures to be square

    filename: Name of file relative to base directory (usually will be 'resources/file.png')
    dim: Dimension of the image (MUST BE SQUARE)
    """
    def set_texture(self, filename, dim):
        self.texture_dim = dim
        self.texture = Image.open(filename)
        self.texture = self.texture.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
        texture_bytes = self.texture.tobytes('raw')

        self.gl_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gl_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, dim, dim, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_bytes)

    """
    Helper method to get a pixel from the texture of any given size.
    
    x: Texture coordinate [0, 1]
    y: Texture coordinate [0, 1]
    Returns: Color from texture
    """
    def get_texture_pixel_color(self, x, y):
        # if no texture is loaded, use white
        if not hasattr(self, 'texture_dim') or not hasattr(self, 'texture'):
            # print(f'{self.name} has no dim/texture, using white!')
            return Color(1, 1, 1, 1)
        # print(f'looking for color at ({x}, {y})')

        # change coordinates to be integers relative to dimensions
        tx = round((self.texture_dim - 1) * x)
        ty = round((self.texture_dim - 1) * y)

        # grab pixel colors from image file
        (r, g, b, a) = self.texture.getpixel((tx, ty))

        return Color(r / 255, g / 255, b / 255, a / 255)

    """
    Attaching a normal map for the texture to the shape.
    Textures will always fill the entire shape, and are not tiled.
    Requires all loaded textures to be square

    filename: Name of file relative to base directory (usually will be 'resources/file.png')
    dim: Dimension of the image (MUST BE SQUARE)
    """
    def set_normal_map(self, filename):
        self.normal_map = Image.open(filename)
        self.normal_map = self.normal_map.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
        self.normal_map = self.normal_map.resize((self.texture_dim, self.texture_dim))

    """
    Helper method to get a pixel from the normal map of any given size.
    
    x: Texture coordinate [0, 1]
    y: Texture coordinate [0, 1]
    Returns: Vector from normal
    """
    def get_normal_map_pixel_vector(self, x, y):
        # if no map is loaded, use white
        if not hasattr(self, 'texture_dim') or not hasattr(self, 'normal_map'):
            return Vector3(0, 0, 0)

        # change coordinates to be integers relative to dimensions
        nmx = round((self.texture_dim - 1) * x)
        nmy = round((self.texture_dim - 1) * y)

        # grab pixel colors from image file
        (x, y, z, _) = self.normal_map.getpixel((nmx, nmy))

        # adjustments to match format
        x = (x / 255) * 2 - 1
        y = (y / 255) * 2 - 1
        z = (z / 255) * 2 - 1

        return Vector3(x, y, z)