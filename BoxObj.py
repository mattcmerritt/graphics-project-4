
from GeomObj import GeomObj
from Vector3 import Vector3
from Hit import Hit
from OpenGL.GL import *

class BoxObj(GeomObj):
    def __init__(self):
        super().__init__()

    @staticmethod
    def draw_side(slices_x, slices_y):
        """ Draw a plane of the specified dimension.
            The plane is a 2x2 square centered at origin (coordinates go -1 to 1).
            slices_x and slices_y are the number of divisions in each dimension
        """
        dx = 2/slices_x  # Change in x direction
        dy = 2/slices_y  # Change in y direction

        glNormal3f(0, 0, 1)
        y = -1
        for j in range(slices_y):
            glBegin(GL_TRIANGLE_STRIP)
            cx = -1
            for i in range(slices_x):
                glVertex3f(cx, y+dy, 0)
                glVertex3f(cx, y, 0)
                cx += dx
            glVertex3f(1, y+dy, 0)
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

    def render_solid(self, slices=10):
        """ Draw a unit cube with one corner at origin in positive octant."""    
        # Draw side 1 (Front)
        glPushMatrix()
        glTranslate(0, 0, 1)
        BoxObj.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 2 (Back)
        glPushMatrix()
        glRotated(180, 0, 1, 0)
        glTranslate(0, 0, 1)
        BoxObj.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 3 (Left)
        glPushMatrix()
        glRotatef(-90, 0, 1, 0)
        glTranslate(0,0,1)
        BoxObj.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 4 (Right)
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        glTranslate(0,0,1)
        BoxObj.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 5 (Top)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glTranslate(0,0,1)
        BoxObj.draw_side(slices, slices)
        glPopMatrix()

        # Draw side 6 (Bottom)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslate(0,0,1)
        BoxObj.draw_side(slices, slices)
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

        print(f'Ray: {ray}')

        # calculate all of the six intersection point t values
        t_values = [None, None, None, None, None, None]

        if ray.dir.dx != 0:
            t_values[0] = (-1 - ray.source.x) / ray.dir.dx  # left
            t_values[3] = (1 - ray.source.x) / ray.dir.dx   # right
        if ray.dir.dy != 0:
            t_values[1] = (-1 - ray.source.y) / ray.dir.dy  # bottom
            t_values[4] = (1 - ray.source.y) / ray.dir.dy   # top
        if ray.dir.dz != 0:
            t_values[2] = (-1 - ray.source.z) / ray.dir.dz  # front
            t_values[5] = (1 - ray.source.z) / ray.dir.dz   # back

        # calculate the points
        #   if a t value is not found, replace with -inf
        #   if an intersection is not in the face, replace with -inf
        # simultaneously, find the minimum positive t value after calculations
        t_min_i = -1
        t_min = float('inf')

        for i in range(len(t_values)):
            print(f'T_{i}: {t_values[i]}')
            # point checking
            if t_values[i] == None:
                t_values[i] = -float('inf')
            else:
                point = ray.eval(t_values[i])
                print(f'Plane hit: {point}')
                if abs(point.x) >= 1 or abs(point.y) >= 1 or abs(point.z) >= 1:
                    print('Moved to negative inf')
                    t_values[i] = -float('inf')
            # min tracking
            if t_values[i] >= 0 and t_values[i] < t_min:
                t_min = t_values[i]
                t_min_i = i
            
        print(f'T_min: {t_min}')

        if t_min_i < 0:
            return False
        
        best_hit.t = t_min
        best_hit.point = ray.eval(t_min)
        best_hit.norm = normals[t_min_i]
        best_hit.norm.normalize()   # stress relief normalization
        best_hit.obj = self
        return True

    # TODO: handled by local_intersect
    # def compute_normal(self, point):
    #     normal = Vector3(0, 0, 0)
