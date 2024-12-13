
import math
from GeomObj import GeomObj
from Vector3 import Vector3
from Hit import Hit
from OpenGL.GL import *
from OpenGL.GLU import *

class CylinderObj(GeomObj):
    def __init__(self, resolution=100):
        super().__init__()

        self.tube = gluNewQuadric()
        self.resolution = resolution
        gluQuadricDrawStyle(self.tube, GLU_FILL)
        gluQuadricTexture(self.tube, GL_TRUE)
        gluQuadricNormals(self.tube, GLU_SMOOTH) 

    def render_solid(self, slices=10):
        """ Draw a cylinder aligned at on the z-axis with radius 1 and height 1."""    
        gluCylinder(self.tube, 1, 1, 1, self.resolution, self.resolution)

    def local_intersect(self, ray, best_hit):
        """
        explanation of logic:
        the cylinder can be defined by the equation
        px**2 + py**2 = 1

        let the origin of the ray be (sx, sy, sz) and (dx, dy, dz) be the direction vector
        any point on the ray can be defined with the following parametric equations:
          px = sx + t*dx
          py = sy + t*dy
          pz = sz + t*dz

        with this information, we can find the point where the ray hits the cylinder by
          by setting px, py, or pz equal the value from the cylinder equation.

        this gives us:
          (sx + t*dx)**2 + (sy + t*dy) = 1
          sx**2 + 2*sx*dx*t + dx**2*t**2 + sy**2 + 2*sy*dy*t + dy**2*t**2 = 1
          sx**2 + 2*sx*dx*t + dx**2*t**2 + sy**2 + 2*sy*dy*t + dy**2*t**2 - 1 = 0
          (dx**2 + dy**2)*t**2 + (2*sx*dx + 2*sy*dy)*t + (a**2 + c**2 - 1) = 0
        
        we can then use the quadratic formula to solve this equation for t:
          t = (-(2*sx*dx + 2*sy*dy) +- sqrt((2*sx*dx + 2*sy*dy)**2 - 4*(dx**2 + dy**2)*(a**2 + c**2 - 1))) / 2*(dx**2 + dy**2)
          t = (2*(-sx*dx - sy*dy) +- sqrt(4*sx**2*dx**2 + 8*sx*dx*sy*dy + 4*sy**2*dy**2 - 4*sx**2*dx**2 - 4*dx**2*sy**2 + 4*dx**2 - 4*sx**2*dy**2 - 4*sy**2*dy**2 + 4*dy**2)) / 2*(dx**2 + dy**2)
          t = (2*(-sx*dx - sy*dy) +- sqrt(8*sx*dx*sy*dy - 4*dx**2*sy**2 + 4*dx**2 - 4*sx**2*dy**2 + 4*dy**2)) / 2*(dx**2 + dy**2)
          t = (2*(-sx*dx - sy*dy) +- 2*sqrt(2*sx*dx*sy*dy - dx**2*sy**2 + dx**2 - sx**2*dy**2 + dy**2)) / 2*(dx**2 + dy**2)
          t = (-sx*dx - sy*dy +- sqrt(2*sx*dx*sy*dy - dx**2*sy**2 + dx**2 - sx**2*dy**2 + dy**2)) / (dx**2 + dy**2)

        where t1 uses the smaller value (-), and t2 uses the larger value (+), or:
          t1 = (-sx*dx -sy*dy - sqrt(2*sx*dx*sy*dy - dx**2*sy**2 + dx**2 - sx**2*dy**2 + dy**2)) / (dx**2 + dy**2)
          t2 = (-sx*dx -sy*dy + sqrt(2*sx*dx*sy*dy - dx**2*sy**2 + dx**2 - sx**2*dy**2 + dy**2)) / (dx**2 + dy**2)

        however, we should check the discriminant beforehand to ensure we have two real solutions.
          if we do not have any real solutions (discriminant is negative), there is no collision.
          if we have one real solution (discriminant is 0), there is only one collision point (line is tangent to the cylinder).
          disc = 2*sx*dx*sy*dy - dx**2*sy**2 + dx**2 - sx**2*dy**2 + dy**2
          t1 = (-sx*dx -sy*dy - sqrt(disc)) / (dx**2 + dy**2)
          t2 = (-sx*dx -sy*dy + sqrt(disc)) / (dx**2 + dy**2)

        if t1 != t2 and both exist, the lower of t1 and t2 is the entrance point, and the other is the exit point.
        """

        # calculate (simplified) discriminant to figure out number of solutions
        disc = 2*ray.source.x*ray.dir.dx*ray.source.y*ray.dir.dy - ray.dir.dx**2*ray.source.y**2 + ray.dir.dx**2 - ray.source.x**2*ray.dir.dy**2 + ray.dir.dy**2

        # if no real solutions
        if disc < 0:
            return False

        # find real solutions, lower one is entry point
        t1 = (-ray.source.x*ray.dir.dx - ray.source.y*ray.dir.dy - math.sqrt(disc)) / (ray.dir.dx**2 + ray.dir.dy**2)
        t2 = (-ray.source.x*ray.dir.dx - ray.source.y*ray.dir.dy + math.sqrt(disc)) / (ray.dir.dx**2 + ray.dir.dy**2)
        t_min = min(t1, t2)

        # if solution worse than existing
        if (t_min >= best_hit.t and best_hit.t != -1):
            return False
          
        # fail if solution point does not collide with a valid z coordinate for the cylinder
        if ray.source.z + t_min * ray.dir.dz < 0 or ray.source.z + t_min * ray.dir.dz > 1:
            return False
        
        # else new solution
        best_hit.t = t_min
        best_hit.point = ray.eval(t_min)
        best_hit.norm = Vector3(best_hit.point.x, best_hit.point.y, best_hit.point.z)
        best_hit.norm.normalize()   # stress relief normalization
        best_hit.obj = self
        return True