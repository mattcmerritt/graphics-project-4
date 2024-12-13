
from GeomObj import GeomObj
from Vector3 import Vector3
from Hit import Hit
from OpenGL.GL import *

class BoxObj(GeomObj):
    def __init__(self):
        super().__init__()

    def draw_side(self, slices_x, slices_y):
        """ Draw a plane of the specified dimension.
            The plane is a 2x2 square centered at origin (coordinates go -1 to 1).
            slices_x and slices_y are the number of divisions in each dimension
        """
        textured = hasattr(self, 'texture')

        if textured:
            glBindTexture(GL_TEXTURE_2D, self.gl_texture)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE) # GL_MODULATE for mutliplicative blending
            glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glEnable(GL_TEXTURE_2D) # Enable/Disable each time or OpenGL ALWAYS expects texturing!

        dx = 2/slices_x  # Change in x direction
        dy = 2/slices_y  # Change in y direction

        glNormal3f(0, 0, 1)
        y = -1
        for j in range(slices_y):
            glBegin(GL_TRIANGLE_STRIP)
            cx = -1
            for i in range(slices_x):
                if textured: glTexCoord2f(cx * 1/2 + 0.5, (y+dy) * 1/2 + 0.5)
                glVertex3f(cx, y+dy, 0)
                if textured: glTexCoord2f(cx * 1/2 + 0.5, y * 1/2 + 0.5)
                glVertex3f(cx, y, 0)
                cx += dx
            if textured: glTexCoord2f(1, (y+dy) * 1/2 + 0.5)
            glVertex3f(1, y+dy, 0)
            if textured: glTexCoord2f(1, y * 1/2 + 0.5)
            glVertex3f(1, y, 0)
            glEnd()
            y += dy

        # Uncomment if you want to "see" the normal
        # isEnabled = glIsEnabled(GL_LIGHTING)
        # if isEnabled: glDisable(GL_LIGHTING)
        # glBegin(GL_LINES)
        # glColor3f(1,1,1)
        # glVertex(0, 0, 0)
        # glVertex(0, 0, 1)
        # glEnd()
        # if isEnabled: glEnable(GL_LIGHTING)

        if textured: glDisable(GL_TEXTURE_2D)

    def render_solid(self, slices=10):
        """ Draw a unit cube with one corner at origin in positive octant."""    
        # Draw side 1 (Back)
        glPushMatrix()
        glTranslate(0, 0, 1)
        glScale(-1, 1, 1)
        self.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 2 (Front)
        glPushMatrix()
        glRotated(180, 0, 1, 0)
        glTranslate(0, 0, 1)
        glScale(1, -1, 1)
        self.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 3 (Left)
        glPushMatrix()
        glRotatef(-90, 0, 1, 0)
        glTranslate(0,0,1)
        glRotatef(-90, 0, 0, 1)
        self.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 4 (Right)
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        glTranslate(0,0,1)
        glRotatef(90, 0, 0, 1)
        self.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 5 (Top)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glTranslate(0,0,1)
        self.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 6 (Bottom)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslate(0,0,1)
        self.draw_side(slices, slices)
        glPopMatrix()

    def local_intersect(self, ray, best_hit):
        """
        explanation of logic:
        each of the faces can be defined by the following planes:
          x = -1 (left)       x = 1 (right)
          y = -1 (bottom)     y = 1 (top)
          z = -1 (front)      z = 1 (back)

        let the origin of the ray be (sx, sy, sz) and (dx, dy, dz) be the direction vector
        any point on the ray can be defined with the following parametric equations:
          px = sx + t * dx
          py = sy + t * dy
          pz = sz + t * dz

        with this information, we can find the point where the ray hits the plane by
          by setting px, py, or pz equal the value from the plane equation.
        for example, working with the front:
          -1 = sz + t * dz 
              or
          t = (-1 - sx) / dx
        NOTE: for this to work, need special cases for when ray is parallel to plane

        with the t values, the points are computed, and each coordinate must fall on [-1, 1]
          if a coordinate is outside these bounds, the ray misses the face

        using the t values for each face, the lowest positive t value is yields the point of
          of first contact, and is used to determine which normal is returned based on the face hit
        """

        # normals for each face
        normals = [
            Vector3(-1, 0, 0),  # right
            Vector3(0, -1, 0),  # bottom
            Vector3(0, 0, -1),  # front
            Vector3(1, 0, 0),   # left
            Vector3(0, 1, 0),   # top
            Vector3(0, 0, 1),   # back
        ]

        # calculate all of the six intersection point t values
        t_values = [None, None, None, None, None, None]
        p_values = [None, None, None, None, None, None]

        if ray.dir.dx != 0:
            t_values[0] = (-1 - ray.source.x) / ray.dir.dx              # left
            p_values[0] = ray.eval(t_values[0]) ; p_values[0].x = -1    # prevent round off in irrelevant dimension
            t_values[3] = (1 - ray.source.x) / ray.dir.dx               # right
            p_values[3] = ray.eval(t_values[3]) ; p_values[3].x = 1     # prevent round off in irrelevant dimension
        if ray.dir.dy != 0:
            t_values[1] = (-1 - ray.source.y) / ray.dir.dy              # bottom
            p_values[1] = ray.eval(t_values[1]) ; p_values[1].y = -1    # prevent round off in irrelevant dimension
            t_values[4] = (1 - ray.source.y) / ray.dir.dy               # top
            p_values[4] = ray.eval(t_values[4]) ; p_values[4].y = 1     # prevent round off in irrelevant dimension
        if ray.dir.dz != 0:
            t_values[2] = (-1 - ray.source.z) / ray.dir.dz              # front
            p_values[2] = ray.eval(t_values[2]) ; p_values[2].z = -1    # prevent round off in irrelevant dimension
            t_values[5] = (1 - ray.source.z) / ray.dir.dz               # back
            p_values[5] = ray.eval(t_values[5]) ; p_values[5].z = 1     # prevent round off in irrelevant dimension

        # calculate the points
        #   if a t value is not found, replace with -inf
        #   if an intersection is not in the face, replace with -inf
        # simultaneously, find the minimum positive t value after calculations
        t_min_i = -1
        t_min = float('inf')

        for i in range(len(t_values)):
            # point checking
            if t_values[i] == None:
                t_values[i] = -float('inf')
            else:
                if abs(p_values[i].x) > 1 or abs(p_values[i].y) > 1 or abs(p_values[i].z) > 1:
                    t_values[i] = -float('inf')
            # min tracking
            if t_values[i] >= 0 and t_values[i] < t_min:
                t_min = t_values[i]
                t_min_i = i

        if t_min_i < 0 or (t_min >= best_hit.t and best_hit.t != -1):
            return False
        
        best_hit.t = t_min
        best_hit.point = ray.eval(t_min)
        best_hit.norm = normals[t_min_i]
        best_hit.norm.normalize()   # stress relief normalization
        best_hit.obj = self

        # texturing
        # TODO: improve tiling with rotations
        
        # based on what plane we are working in, convert hit to 2D point
        # the conversion to texture coordinates uses the following equation:
        # tex_pos = world_pos * tex_scale / world_scale - world_min_pos * tex_scale / world_scale
        if t_min_i == 0:    # right plane (-x, YZ plane)
            world_x = best_hit.point.y
            world_y = best_hit.point.z
            texture_x = 1 - (world_x * 1/2 - (-1 * 1/2))
            texture_y = world_y * 1/2 - (-1 * 1/2)
        elif t_min_i == 1:  # bottom plane (-y, XZ plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.z
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = world_y * 1/2 - (-1 * 1/2)
        elif t_min_i == 2:  # front plane (-z, XY plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.y
            texture_x = 1 - (world_x * 1/2 - (-1 * 1/2))
            texture_y = 1 - (world_y * 1/2 - (-1 * 1/2))
        elif t_min_i == 3:    # left plane (+x, YZ plane)
            world_x = best_hit.point.y
            world_y = best_hit.point.z
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = world_y * 1/2 - (-1 * 1/2)
        elif t_min_i == 4:  # top plane (+y, XZ plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.z
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = 1 - (world_y * 1/2 - (-1 * 1/2))
        elif t_min_i == 5:  # back plane (+z, XY plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.y
            texture_x = 1 - (world_x * 1/2 - (-1 * 1/2))
            texture_y = world_y * 1/2 - (-1 * 1/2)

        # grab color from pixel map
        best_hit.texture_color = self.get_texture_pixel_color(texture_x, texture_y)

        # based on what plane we are working in, convert hit to 2D point
        # the conversion to texture coordinates uses the following equation:
        # tex_pos = world_pos * tex_scale / world_scale - world_min_pos * tex_scale / world_scale
        # note: the tiling transformations are removed here to not make the normal map lighting look strange
        if t_min_i == 0:    # right plane (-x, YZ plane)
            world_x = best_hit.point.y
            world_y = best_hit.point.z
            texture_x = world_y * 1/2 - (-1 * 1/2)
            texture_y = world_x * 1/2 - (-1 * 1/2)
        elif t_min_i == 1:  # bottom plane (-y, XZ plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.z
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = world_y * 1/2 - (-1 * 1/2)
        elif t_min_i == 2:  # front plane (-z, XY plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.y
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = world_y * 1/2 - (-1 * 1/2)
        elif t_min_i == 3:    # left plane (+x, YZ plane)
            world_x = best_hit.point.y
            world_y = best_hit.point.z
            texture_x = world_y * 1/2 - (-1 * 1/2)
            texture_y = world_x * 1/2 - (-1 * 1/2)
        elif t_min_i == 4:  # top plane (+y, XZ plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.z
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = world_y * 1/2 - (-1 * 1/2)
        elif t_min_i == 5:  # back plane (+z, XY plane)
            world_x = best_hit.point.x
            world_y = best_hit.point.y
            texture_x = world_x * 1/2 - (-1 * 1/2)
            texture_y = world_y * 1/2 - (-1 * 1/2)

        # adjust vector for norm based on normal map
        best_hit.norm = best_hit.norm.__add__(self.get_normal_map_pixel_vector(texture_x, texture_y))
        
        return True