import bpy
import math
import random

class Ground:
    """Class defining the ground.
    The ground is caracterized by its size and by its altitude
    in function of x and y."""
    
    def __init__(self, x_size, y_size, relief_complexity,
        relief_amplitude):
        """Create a new ground with its size and relief level.
        The relief complexity is a integer between 0 (no relief)
        an 2."""
        
        # save the values
        self.x_size = x_size
        self.y_size = y_size
        
        # define altitude_f
        if relief_complexity == 0:
            self.altitude_f = lambda x, y: 0
        elif relief_complexity == 1:
            self.altitude_f = Ground.mound_altitude_f(0, 0,
                                                      relief_amplitude)
        else:
            x0 = random.uniform(-x_size/2, x_size/2)
            x1 = random.uniform(-x_size/2, x_size/2)
            x2 = random.uniform(-x_size/2, x_size/2)
            y0 = random.uniform(-x_size/2, x_size/2)
            y1 = random.uniform(-x_size/2, x_size/2)
            y2 = random.uniform(-x_size/2, x_size/2)
            altitude = relief_amplitude/2
            self.altitude_f = (lambda x, y:
                Ground.mound_altitude_f(x0, y0, altitude)(x, y)
                + Ground.mound_altitude_f(x1, y1, altitude)(x, y)
                + Ground.mound_altitude_f(x2, y2, altitude)(x, y))
        
    
    @staticmethod
    def mound_altitude_f(x_0, y_0, altitude, sharpening=0.003):
        """Create a function giving an altitude that creates a mound
        centered in x_0, y_0 of with the given altitude and
        sharpening."""
        return (lambda x, y:
            altitude*math.exp(-sharpening*((x-x_0)**2+(y-y_0)**2)))
