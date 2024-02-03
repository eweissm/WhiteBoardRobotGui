#this code will contain all necessary functions to take a bmp and convert it into 2d Gcode

#How the process will work:
# 1) convert image to black and white
# 2)use thresholding to outine features
# 3) Trace image using Potrace --> gives list of paths

from PIL import Image
import numpy as np
import potrace
import matplotlib.pyplot as plt
import math

def Img_to_Gcode(OriginalImageAddress):

    bitmap = Image.open(OriginalImageAddress)

    ary = np.array(bitmap)

    bitmap = np.array(bitmap).reshape([ary.shape[0], ary.shape[1]])
    bitmap = np.dot((bitmap > 128).astype(float), 1)
    im = Image.fromarray(bitmap.astype(np.uint8))
    bmp = potrace.Bitmap(bitmap)  # convert image array  into Pypotrace bitmap object

    path = bmp.trace(alphamax = 1)

    xvals = []
    yvals = []

    #print(path)
    for curve in path:
        #print("start_point =", curve.start_point)
        for segment in curve:
           # print(segment)
            end_point_x, end_point_y = segment.end_point
            if segment.is_corner:
                c_x, c_y = segment.c
                xvals.append(c_x)
                yvals.append(c_y)
            else:
                c1_x, c1_y = segment.c1
                c2_x, c2_y = segment.c2

                temp_x_list, temp_y_list = bezier_to_points(xvals[-1], yvals[-1], c1_x, c1_y,c2_x, c2_y, end_point_x, end_point_y)
                xvals.append(temp_x_list)
                yvals.append(temp_y_list)

   # print(xvals)

    # plot
    fig, ax = plt.subplots()
    ax.plot(xvals, yvals)
    plt.show()

def bezier_to_points(xvals, yvals, c1_x, c1_y,c2_x, c2_y, end_point_x, end_point_y):
    numSegments = 10
    for t in np.linspace(0, 1, num=numSegments):
        x = (
            p1[0] * math.pow(1 - t, 3)
            + 3 * p2[0] * math.pow(1 - t, 2) * t
            + 3 * p3[0] * (1 - t) * math.pow(t, 2)
            + p4[0] * math.pow(t, 3)
        )
        y = (
            p1[1] * math.pow(1 - t, 3)
            + 3 * p2[1] * math.pow(1 - t, 2) * t
            + 3 * p3[1] * (1 - t) * math.pow(t, 2)
            + p4[1] * math.pow(t, 3)
        )
        yield (x, y)

Img_to_Gcode("Example Image.bmp")
