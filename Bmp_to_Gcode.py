#this code will contain all necessary functions to take a bmp and convert it into 2d Gcode

#How the process will work:
# 1) convert image to black and white
# 2)use thresholding to outine features
# 3) Trace image using Potrace --> gives list of paths

#import libs
from PIL import Image
import numpy as np
import potrace
import matplotlib.pyplot as plt
import math
import PIL.ImageOps

def Img_to_Gcode(OriginalImageAddress):
    threshold = 150

    bitmap = Image.open(OriginalImageAddress) # get the bmp as pil image
    bitmap = PIL.ImageOps.invert(bitmap)    #flip colors (makes sure edges arent traced)

    #this section converts bitmap to values from 0 to 1:
    bitmap = np.array(bitmap).reshape([bitmap.height, bitmap.width])
    bitmap= np.flip(bitmap)
    bitmap = np.flip(bitmap,1)
    bitmap = np.dot((bitmap > threshold).astype(float), 1)

    bmp = potrace.Bitmap(bitmap)  # convert image array  into Pypotrace bitmap object

    path = bmp.trace(turdsize = 50 ,turnpolicy= potrace.TURNPOLICY_MINORITY ,alphamax = 1, opticurve =0) # perform trace

    xvals = []
    yvals = []

    #print(path)
    for curve in path:
        for segment in curve:
            if segment.is_corner:
                c_x, c_y = segment.c
                xvals.append(float(c_x))
                yvals.append(float(c_y))
            else:

                try:
                    temp_x_list, temp_y_list = bezier_to_points([xvals[-1],yvals[-1]], segment.c1, segment.c2, segment.end_point)
                    xvals= xvals +temp_x_list
                    yvals = yvals + temp_y_list
                except:
                    temp_x_list, temp_y_list = bezier_to_points(curve.start_point, segment.c1, segment.c2,
                                                                segment.end_point)
                    xvals = xvals + temp_x_list
                    yvals = yvals + temp_y_list

    # plot
    fig, ax = plt.subplots()
    ax.plot(xvals, yvals)
    plt.show()

# Type alias for a point
point = tuple[float, float]
def bezier_to_points(p1: point, p2: point, p3: point, p4: point):
    numSegments = 5

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
    #print(x_list)

    return x_list, y_list

Img_to_Gcode("Example Image.bmp")
