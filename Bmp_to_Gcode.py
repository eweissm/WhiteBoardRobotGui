#this code will contain all necessary functions to take a bmp and convert it into 2d Gcode

#How the process will work:
# 1) convert image to black and white
# 2)use thresholding to outine features
# 3) Trace image using Potrace --> gives list of paths
# 4) turn trace into series of x, y points on distinct curves

#import libs
from PIL import Image, ImageFilter
import numpy as np
import potrace
import matplotlib.pyplot as plt
import math
import PIL.ImageOps

def Img_to_Gcode(bitmap):
    threshold = 50

    bitmap = PIL.ImageOps.invert(bitmap)    #flip colors (makes sure edges arent traced)

    #this section converts bitmap to values from 0 to 1:
    bitmap = np.array(bitmap).reshape([bitmap.height, bitmap.width])
    bitmap= np.flip(bitmap)
    bitmap = np.flip(bitmap,1)
    bitmap = np.dot((bitmap > threshold).astype(float), 1)

    bmp = potrace.Bitmap(bitmap)  # convert image array  into Pypotrace bitmap object

    path = bmp.trace(turdsize = 0 ,turnpolicy= potrace.TURNPOLICY_MINORITY ,alphamax = 1, opticurve =0) # perform trace

    #lists for discretized points from the trace
    xvals = []
    yvals = []

    Curves_X_Cords = []
    Curves_Y_Cords = []

    #cyle through curves and segements in the curves
    for curve in path:
        firstSegment = True

        for segment in curve:
            if segment.is_corner:
                c_x, c_y = segment.c
                xvals.append(float(c_x))
                yvals.append(float(c_y))
            else:
                if not firstSegment:
                    temp_x_list, temp_y_list = bezier_to_points([xvals[-1], yvals[-1]], segment.c1, segment.c2, segment.end_point)
                    xvals= xvals + temp_x_list
                    yvals = yvals + temp_y_list
                else:
                    temp_x_list, temp_y_list = bezier_to_points(curve.start_point, segment.c1, segment.c2,
                                                                segment.end_point)
                    xvals = xvals + temp_x_list
                    yvals = yvals + temp_y_list

            firstSegment = False
        Curves_X_Cords.append(xvals)
        Curves_Y_Cords.append(yvals)
        xvals=[]
        yvals = []


    # plot
    fig, ax = plt.subplots()

    for i in range(len(Curves_X_Cords)):
        ax.plot(Curves_X_Cords[i], Curves_Y_Cords[i], linewidth=.7)

    plt.show()


    #print(list(zip(xvals,yvals)))
# Type alias for a point
point = tuple[float, float]

# function converts bezierr segment into set of point
def bezier_to_points(p1: point, p2: point, p3: point, p4: point):
    # MaxSectionLength = 10
    # approxBezierLength = math.sqrt( (p1[0] - p4[0])**2 + (p1[0] - p4[1])**2 )
    # numSegments = math.ceil(approxBezierLength/MaxSectionLength)
    numSegments=5
    x_list =[]
    y_list = []
    for t in np.linspace(0, 1, num=numSegments):
        x_list.append(float(
                p1[0] * math.pow(1 - t, 3)
                + 3 * p2[0] * math.pow(1 - t, 2) * t
                + 3 * p3[0] * (1 - t) * math.pow(t, 2)
                + p4[0] * math.pow(t, 3)
        ))
        y_list.append(float(
                p1[1] * math.pow(1 - t, 3)
                + 3 * p2[1] * math.pow(1 - t, 2) * t
                + 3 * p3[1] * (1 - t) * math.pow(t, 2)
                + p4[1] * math.pow(t, 3)
        ))
    x_list.pop(0)
    y_list.pop(0)

    #print(x_list)

    return x_list, y_list

#bitmap = Image.open("Example Image.bmp") # get the bmp as pil image
#Img_to_Gcode(bitmap)
