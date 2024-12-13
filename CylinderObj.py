
import math
from GeomObj import GeomObj
from Vector3 import Vector3
from Hit import Hit
from Color import Color
from OpenGL.GL import *
from OpenGL.GLU import *

class CylinderObj(GeomObj):
    def __init__(self, r_start=1, r_end=1, height=1, resolution=100):
        super().__init__()

        self.tube = gluNewQuadric()
        self.resolution = resolution
        self.r_start = r_start
        self.r_end = r_end
        self.height = height
        gluQuadricDrawStyle(self.tube, GLU_FILL)
        gluQuadricTexture(self.tube, GL_TRUE)
        gluQuadricNormals(self.tube, GLU_SMOOTH) 

    def render_solid(self):
        """ Draw a cylinder aligned at on the z-axis with radius r_start at one end, r_end at the other and height height."""    
        gluCylinder(self.tube, self.r_start, self.r_end, self.height, self.resolution, self.resolution)

    def local_intersect(self, ray, best_hit):
        """
        explanation of logic:
        the cylinder can be defined by the equation
          px**2 + py**2 = r**2
        
        where r is linearly interpolated from the z value as such:
          r = (r_end - r_start)/height * pz + r_start
          r = (r_end - r_start)/height * (sz + t*dz) + r_start

        for simplicity's sake, we add the following substitution:
          r_lerp = (r_end - r_start)/height 
        so
          r = r_lerp*(sz + t*dz) + r_start
          r = sz*r_lerp + dz*r_lerp*t + r_start

        let the origin of the ray be (sx, sy, sz) and (dx, dy, dz) be the direction vector
        any point on the ray can be defined with the following parametric equations:
          px = sx + t*dx
          py = sy + t*dy
          pz = sz + t*dz

        with this information, we can find the point where the ray hits the cylinder by
          by setting px, py, and pz equal the value from the cylinder equation.

        this gives us:
          (sx + t*dx)**2 + (sy + t*dy) = (sz*r_lerp + dz*r_lerp*t + r_start)**2
          sx**2 + 2*sx*dx*t + dx**2*t**2 + sy**2 + 2*sy*dy*t + dy**2*t**2 = sz**2*r_lerp**2 + 2*sz*dz*r_lerp**2*t + 2*sz*r_lerp*r_start + dz**2*r_lerp**2*t**2 + 2*dz*r_lerp*r_start*t + r_start**2
          sx**2 + 2*sx*dx*t + dx**2*t**2 + sy**2 + 2*sy*dy*t + dy**2*t**2 - sz**2*r_lerp**2 - 2*sz*dz*r_lerp**2*t - 2*sz*r_lerp*r_start - dz**2*r_lerp**2*t**2 - 2*dz*r_lerp*r_start*t - r_start**2 = 0
          (dx**2 + dy**2 - dz**2*r_lerp**2)*t**2 + (2*sx*dx + 2*sy*dy - 2*sz*dz*r_lerp**2 - 2*dz*r_lerp*r_start)*t + (sx**2 + sy**2 - sz**2*r_lerp**2 - 2*sz*r_lerp*r_start - r_start**2) = 0
          
        so now we can use the quadratic formula with
          a = dx**2 + dy**2 - dz**2*r_lerp**2
          b = 2*sx*dx + 2*sy*dy - 2*sz*dz*r_lerp**2 - 2*dz*r_lerp*r_start
          c = sx**2 + sy**2 - sz**2*r_lerp**2 - 2*sz*r_lerp*r_start - r_start**2

        we should check the discriminant beforehand to ensure there is a collision
          disc = b**2 - 4*a*c
          sqrt_disc = math.sqrt(disc) # saves calculation time

        gather the two (or one if the same) solutions
          t1 = (-b - sqrt_disc) / (2*a)
          t2 = (-b + sqrt_disc) / (2*a)

        if t1 != t2 and both exist, the lower of t1 and t2 is the entrance point, and the other is the exit point.
        if t1 == t2, there is only a collision point (ray is tangent to cylinder).
        """

        # define r_lerp
        r_lerp = (self.r_end - self.r_start)/self.height    # this is a factor, not actually the radius!

        # set up for quadratic formula
        a = ray.dir.dx**2 + ray.dir.dy**2 - ray.dir.dz**2*r_lerp**2
        b = 2*ray.source.x*ray.dir.dx + 2*ray.source.y*ray.dir.dy - 2*ray.source.z*ray.dir.dz*r_lerp**2 - 2*ray.dir.dz*r_lerp*self.r_start
        c = ray.source.x**2 + ray.source.y**2 - ray.source.z**2*r_lerp**2 - 2*ray.source.z*r_lerp*self.r_start - self.r_start**2

        # calculate discriminant to figure out number of solutions
        disc = b**2 - 4*a*c

        # if no real solutions
        if disc < 0:
            return False

        sqrt_disc = math.sqrt(disc) # saves calculation time

        # find real solutions, lower one is entry point
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        (t_min, t_max) = (t1, t2) if t1 < t2 else (t2, t1)

        # figure if inside or outside
        invert_for_inside = 1           # default no inversion (outside)

        # test t_min, if t_min is ok (not behind start and within bounded cylinder) we are outside
        if t_min < 0 or (ray.source.z + t_min * ray.dir.dz < 0 or ray.source.z + t_min * ray.dir.dz > self.height):
            invert_for_inside = -1        # since test failed, must be inside, or no valid collision
        # assuming t_max doesn't fail the same test, we are inside
        # if it does fail, it won't draw anyways - no need to change anything again

        # clamp
        if ray.source.z + t1 * ray.dir.dz < 0 or ray.source.z + t1 * ray.dir.dz > self.height:
            t1 = -1   # fail if solution point does not collide with a valid z coordinate for the cylinder
        if ray.source.z + t2 * ray.dir.dz < 0 or ray.source.z + t2 * ray.dir.dz > self.height:
            t2 = -1   # fail if solution point does not collide with a valid z coordinate for the cylinder

        # compare after clamping to figure out which point to use
        t_min = min(t1, t2) if t1 > 0 and t2 > 0 else max(t1, t2)

        # if solution is behind camera or worse than existing
        if t_min < 0 or (t_min >= best_hit.t and best_hit.t != -1):
            return False
        
        # else new solution
        best_hit.t = t_min
        best_hit.point = ray.eval(t_min)
        best_hit.norm = Vector3(invert_for_inside * best_hit.point.x, invert_for_inside * best_hit.point.y, invert_for_inside * (self.r_end-self.r_start) / 2)
        best_hit.norm.normalize()   # stress relief normalization
        best_hit.obj = self
        best_hit.texture_color = Color(1, 1, 1, 1) # defaults to white
        return True